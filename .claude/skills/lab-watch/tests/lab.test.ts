import { describe, expect, mock, test } from 'claude-code/testing'
import type { On } from 'claude-code'

import {
  countedVerdicts,
  experimentOf,
  isBlenderRun,
  judgedVerdicts,
  parseBudget,
  parseJudgement,
  parseScore,
  parseTarget,
  roundStart,
  sparkline,
} from '../hooks/lab'

describe('parsing the lab files', () => {
  test('scores in each review format the lab has used', () => {
    expect(parseScore('# Review v14\n\n**Score:** 6.3 / 10\n')).toBe(6.3)
    expect(parseScore('# Review v06\n\n## 1. Score: 7.2 / 10\n\nSphere 6.5')).toBe(7.2)
    expect(parseScore('## Score: 8.4 / 10')).toBe(8.4)
    expect(parseScore('## What works\nno score here')).toBe(null)
  })

  test('budget and target from BRIEF.md', () => {
    const brief = '## Target\n\nScore 8.5 from the reviewer.\n\n## Budget\n\n16 review rounds (10, plus 6 for the fork).\n'
    expect(parseBudget(brief)).toBe(16)
    expect(parseTarget(brief)).toBe(8.5)
    expect(parseBudget('no budget')).toBe(10)
  })

  test('only real Blender runs count', () => {
    expect(isBlenderRun('tools/blender.sh experiments/x/scripts/build.py --out v03')).toBe(true)
    expect(isBlenderRun('BLEND=a.blend VERBOSE=1 tools/blender.sh t.py')).toBe(true)
    expect(isBlenderRun('bash tools/sweep.sh build.py s1 "a=1"')).toBe(true)
    expect(isBlenderRun("grep -q 'tools/blender.sh' transcript")).toBe(false)
  })

  test('writes and lab runs switch the experiment, reads do not', () => {
    expect(experimentOf('Write', { file_path: '/r/experiments/wax-seal/PROGRESS.md' })).toBe('wax-seal')
    expect(experimentOf('Read', { file_path: '/r/experiments/wax-seal/PROGRESS.md' })).toBe(null)
    expect(experimentOf('Bash', { command: 'python3 tools/review_round.py clouds v04 10,20' })).toBe('clouds')
    expect(experimentOf('Bash', { command: 'cat experiments/clouds/BRIEF.md' })).toBe(null)
  })

  test('sparkline keeps gaps for unscored reviews', () => {
    expect(sparkline([6, null, 7])).toBe('▁ █')
  })
})

describe('the counted rules', () => {
  const s = (...xs: number[]) => xs.map((score, i) => ({ version: `v0${i + 1}`, score }))

  test('slope flat from round 6', () => {
    const v = countedVerdicts({ scores: s(5, 6, 6.4, 6.3, 6.5, 6.6), reviewCount: 6, budget: 10, isForked: false })
    expect(v.map(x => x.rule)).toEqual(['slope'])
  })

  test('a rising slope and a fork are left alone', () => {
    expect(countedVerdicts({ scores: s(5, 5.5, 5.8, 6.2, 6.5, 6.9), reviewCount: 6, budget: 10, isForked: false })).toEqual([])
    expect(countedVerdicts({ scores: s(5, 6, 6.4, 6.3, 6.5, 6.6), reviewCount: 6, budget: 16, isForked: true })).toEqual([])
  })

  test('budget spent', () => {
    const v = countedVerdicts({ scores: s(5, 6), reviewCount: 10, budget: 10, isForked: false })
    expect(v.map(x => x.rule)).toEqual(['budget'])
  })
})

describe('the read rules', () => {
  test('target and repeat rules need three reviews', () => {
    const j = parseJudgement('{"wholeFormWrong": true, "wholeFormQuote": "reads as a bucket", "missedEveryRound": ["p5"], "repeatedComplaint": "gaps not black"}')
    expect(j).not.toBe(null)
    if (!j) return
    expect(judgedVerdicts(j, ['v01', 'v02']).map(x => x.rule)).toEqual(['whole-form'])
    expect(judgedVerdicts(j, ['v01', 'v02', 'v03']).map(x => x.rule)).toEqual(['whole-form', 'target', 'repeat'])
  })

  test('an unreadable reply is no judgement', () => {
    expect(parseJudgement('Sorry, I cannot')).toBe(null)
  })
})

// A small experiment folder in memory, answered beneath the plugin.
const ROOT = '/lab'
const EXP = `${ROOT}/experiments/demo`

const review = (v: string, score: number) =>
  `# Review ${v}\n\n**Score:** ${score} / 10\n\n## Targets\n\n- Glass upper (69, 81, 105): **missed**\n\n## Problems, ranked\n\n1. **The glass reads as CG.** Fix it.\n`

const world = (on: On) => {
  const files = new Map<string, { text: string; mtimeMs: number }>()
  let t = 1000
  const put = (path: string, text: string) => files.set(path, { text, mtimeMs: (t += 1000) })
  put(`${ROOT}/tools/blender.sh`, '#!/bin/bash')
  put(`${EXP}/BRIEF.md`, '## Target\n\nScore 8.5 from the reviewer.\n\n## Budget\n\n10 review rounds.\n')
  put(`${EXP}/PROGRESS.md`, '# demo\n')
  put(`${EXP}/RESEARCH.md`, '## Sources\n\n- https://example.com\n')
  put(`${EXP}/renders/v01.png`, '')
  put(`${EXP}/reviews/review_v01.md`, review('v01', 5.5))
  put(`${EXP}/reviews/review_v02.md`, review('v02', 6.0))

  const isDir = (path: string) => [...files.keys()].some(k => k.startsWith(`${path}/`))
  const missing = { deny: 'ENOENT' }

  on('fs.read', ($, e) => {
    const f = files.get(e.path)
    return f ? { value: f.text } : missing
  })
  on('fs.exists', ($, e) => ({ value: files.has(e.path) || isDir(e.path) }))
  on('fs.stat', ($, e) => {
    const f = files.get(e.path)
    if (f) return { value: { kind: 'file' as const, size: f.text.length, mtimeMs: f.mtimeMs, isLink: false } }
    return isDir(e.path) ? { value: { kind: 'dir' as const, size: 0, mtimeMs: 0, isLink: false } } : missing
  })
  on('fs.list', ($, e) => {
    const seen = new Map<string, { name: string; kind: 'file' | 'dir'; size: number; mtimeMs: number; isLink: boolean }>()
    for (const [k, f] of files) {
      if (!k.startsWith(`${e.path}/`)) continue
      const rest = k.slice(e.path.length + 1)
      const name = rest.split('/')[0] ?? rest
      const isFile = !rest.includes('/')
      seen.set(name, { name, kind: isFile ? 'file' : 'dir', size: 0, mtimeMs: isFile ? f.mtimeMs : 0, isLink: false })
    }
    return { value: [...seen.values()] }
  })
  on('session.root', () => ({ value: ROOT }))
  on('process.run', () => ({ value: { exitCode: 0, stdout: 'PNG image data, 1600 x 900, 8-bit/color RGBA', stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }))
  on('command.register', () => ({ value: { command: 'lab' } }))
  on('ui.open', () => ({ value: { isPlaced: true as const } }))
  on('ui.toast', () => ({ value: undefined }))
  on('session.start', ($, e) => ({ cwd: e.cwd }))
  mock.clock(on)

  const prompts: string[] = []
  on('model.complete', ($, e) => {
    prompts.push(e.prompt)
    return {
      value: {
        isAnswered: true as const,
        text: '{"wholeFormWrong": false, "wholeFormQuote": "", "missedEveryRound": ["Glass upper"], "repeatedComplaint": "glass reads as CG"}',
        usage: { input_tokens: 1, output_tokens: 1, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 },
      },
    } as never
  })

  // The reviewer writes the next review while its Agent call runs.
  on('tool.call', ($, e) => {
    if (e.tool === 'Agent') put(`${EXP}/reviews/review_v03.md`, review('v03', 6.1))
    return { result: 'done' as never }
  })
  return { put, prompts }
}

test('the guard speaks once, after a review that lands this session', async ($, on) => {
  const w = world(on)
  await $.session.start({ cwd: ROOT, surface: 'terminal', isInteractive: true })

  const before = await $.tool.call({ tool: 'Bash', command: 'ls' } as never)
  expect(before.context).toBe(undefined)
  expect(w.prompts.length).toBe(0)

  const after = await $.tool.call({ tool: 'Agent', prompt: 'review', description: 'review v03', subagent_type: 'general-purpose' } as never)
  const text = (after.context ?? []).join('\n')
  expect(text).toContain('review v03 of demo')
  expect(text).toContain('Missed three rounds running (v01–v03): Glass upper')
  expect(text).toContain('"glass reads as CG"')
  expect(w.prompts.length).toBe(1)

  const again = await $.tool.call({ tool: 'Bash', command: 'ls' } as never)
  expect(again.context).toBe(undefined)
  expect(w.prompts.length).toBe(1)
})

test('the pane draws the experiment on the terminal and the desktop', async ($, on) => {
  world(on)
  await $.session.start({ cwd: ROOT, surface: 'terminal', isInteractive: true })
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({
      plugin: 'lab-watch',
      surface,
      component: 'Pane',
      requestId: 'lab',
      props: { title: 'Lab', isFocused: false, bodyColumns: 60, placement: 'dock' } as never,
    })
    expect(await ui.find({ text: /demo/ })).toBeDefined()
    expect(await ui.find({ text: /no-such-text/ })).toBe(undefined)
    expect(await ui.find({ text: /round 2: v01|review round 2 of 10/ })).toBeDefined()
    expect(await ui.find({ text: /5.5 → 6/ })).toBeDefined()
    expect(await ui.find({ text: /2\/10 reviews|2\/\s*10 reviews/ })).toBeDefined()
    await ui.unmount()
  }
})

describe('roundStart', () => {
  test('the newest "## Round ... (from vNN)" heading in PROGRESS.md', () => {
    const progress = '## Setup\n\n## Round two: materials (from v13)\n\ntext\n\n## Round three: the sofa (from v19)\n'
    expect(roundStart(progress)).toBe(19)
  })
  test('no round heading: every review counts', () => {
    expect(roundStart('## Setup\n| v01 | 6.8 |')).toBe(0)
  })
})
