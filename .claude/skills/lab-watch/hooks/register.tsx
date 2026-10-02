import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { GuardResult, RenderInfo, Summary } from '../types'
import {
  bar,
  byVersion,
  countedVerdicts,
  experimentOf,
  guardMessage,
  hasResearch,
  isAnyReview,
  isBlenderRun,
  isForked,
  isVersionRender,
  JUDGE_SYSTEM,
  judgedVerdicts,
  judgePrompt,
  parseBudget,
  parseJudgement,
  parseScore,
  parseTarget,
  reviewFile,
  sparkline,
  versionOf,
} from './lab'

const PANE = 'lab'
const TITLE = 'Lab'

const active = atom({ plugin: 'lab-watch', key: 'active' } as const, null)
const isPinned = atom({ plugin: 'lab-watch', key: 'isPinned' } as const, false)
const summary = atom({ plugin: 'lab-watch', key: 'summary' } as const, null)
const runs = atom({ plugin: 'lab-watch', key: 'runs' } as const, 0)
const startedMs = atom({ plugin: 'lab-watch', key: 'startedMs' } as const, 0)
const minutes = atom({ plugin: 'lab-watch', key: 'minutes' } as const, 0)
const guard = atom({ plugin: 'lab-watch', key: 'guard' } as const, null)
const checked = atom({ plugin: 'lab-watch', key: 'checked' } as const, {})

type $ = EngineInterface

const text = ($: $, path: string) => $.fs.read(path).then(String, () => '')
const list = ($: $, path: string) => $.fs.list(path).catch(() => [])

// Review texts and render sizes, by path and mtime. A reload starts it over.
const cache = new Map<string, unknown>()

const cached = async <T,>(key: string, load: () => Promise<T>): Promise<T> => {
  if (cache.has(key)) return cache.get(key) as T
  const value = await load()
  cache.set(key, value)
  return value
}

const experimentDir = (root: string, name: string) => `${root}/experiments/${name}`

const isExperiment = ($: $, root: string, name: string) =>
  $.fs.exists(`${experimentDir(root, name)}/BRIEF.md`).catch(() => false)

// The experiment whose PROGRESS.md changed last: where the session most likely picks up.
const newestExperiment = async ($: $, root: string): Promise<string | null> => {
  let best: { name: string; t: number } | null = null
  for (const entry of await list($, `${root}/experiments`)) {
    if (entry.kind !== 'dir') continue
    const stat = await $.fs.stat(`${root}/experiments/${entry.name}/PROGRESS.md`).catch(() => null)
    if (stat && (!best || stat.mtimeMs > best.t)) best = { name: entry.name, t: stat.mtimeMs }
  }
  return best?.name ?? null
}

type ReviewText = { version: string; file: string; text: string; mtimeMs: number }

// The scored reviews, oldest first, and how many review_v*.md the budget counts.
const readReviews = async ($: $, dir: string) => {
  const entries = await list($, `${dir}/reviews`)
  const reviews: ReviewText[] = []
  const files = entries
    .filter(e => e.kind === 'file')
    .map(e => ({ e, r: reviewFile(e.name) }))
    .filter((x): x is { e: (typeof entries)[number]; r: NonNullable<typeof x.r> } => x.r !== null)
    .sort((a, b) => byVersion(a.r, b.r))
  for (const { e, r } of files) {
    const path = `${dir}/reviews/${e.name}`
    const body = await cached(`${path}@${e.mtimeMs}`, () => text($, path))
    reviews.push({ version: r.version, file: e.name, text: body, mtimeMs: e.mtimeMs })
  }
  const count = entries.filter(e => e.kind === 'file' && isAnyReview(e.name)).length
  return { reviews, count }
}

const pngSize = async ($: $, path: string) => {
  const run = await $.process.run(['file', path], { timeoutMs: 5000 }).catch(() => null)
  const m = run ? /(\d+)\s*x\s*(\d+)/.exec(run.stdout) : null
  return m ? { width: Number(m[1]), height: Number(m[2]) } : { width: 16, height: 9 }
}

const newestRender = async ($: $, dir: string): Promise<RenderInfo | null> => {
  const renders = (await list($, `${dir}/renders`))
    .filter(e => e.kind === 'file' && isVersionRender(e.name))
    .sort((a, b) => b.mtimeMs - a.mtimeMs)
  const top = renders[0]
  if (!top) return null
  const path = `${dir}/renders/${top.name}`
  const size = await cached(`${path}@${top.mtimeMs}:size`, () => pngSize($, path))
  return { file: top.name, path, mtimeMs: top.mtimeMs, ...size }
}

const scan = async ($: $, root: string, name: string): Promise<Summary | null> => {
  const dir = experimentDir(root, name)
  if (!(await isExperiment($, root, name))) return null
  const [brief, progress, research] = await Promise.all([
    text($, `${dir}/BRIEF.md`),
    text($, `${dir}/PROGRESS.md`),
    text($, `${dir}/RESEARCH.md`),
  ])
  const { reviews, count } = await readReviews($, dir)
  const render = await newestRender($, dir)
  const budget = parseBudget(brief)
  const newestReview = reviews[reviews.length - 1]
  const finals = (await list($, `${dir}/output`)).filter(
    e => e.kind === 'file' && /^FINAL.*\.png$/i.test(e.name),
  )
  const isFinished =
    finals.length > 0 && finals.some(f => f.mtimeMs >= (newestReview?.mtimeMs ?? 0))
  const renderVersion = render ? versionOf(render.file) : null
  const isReviewed = !renderVersion || reviews.some(r => r.version === renderVersion)

  const step = !hasResearch(research, progress)
    ? 'research'
    : !render
      ? 'build'
      : isFinished
        ? 'finished'
        : !isReviewed
          ? `round ${count + 1}: ${renderVersion} awaits review`
          : `review round ${count} of ${budget}`

  return {
    name,
    step,
    scores: reviews.map(r => ({ version: r.version, score: parseScore(r.text) })),
    reviewCount: count,
    budget,
    target: parseTarget(brief),
    isForked: isForked(progress),
    render,
  }
}

// The review-render rules for the newest review: counted ones always, read
// ones through a small model. Its failure only drops the read rules.
const judge = async ($: $, root: string, name: string): Promise<GuardResult | null> => {
  const dir = experimentDir(root, name)
  const [brief, progress] = await Promise.all([
    text($, `${dir}/BRIEF.md`),
    text($, `${dir}/PROGRESS.md`),
  ])
  const { reviews, count } = await readReviews($, dir)
  const newest = reviews[reviews.length - 1]
  if (!newest) return null
  const verdicts = countedVerdicts({
    scores: reviews.map(r => ({ version: r.version, score: parseScore(r.text) })),
    reviewCount: count,
    budget: parseBudget(brief),
    isForked: isForked(progress),
  })
  let note: string | null = null
  const recent = reviews.slice(-3)
  if (recent.length >= 2) {
    const reply = await $.model.complete({
      model: 'haiku',
      system: JUDGE_SYSTEM,
      prompt: judgePrompt(recent),
      maxTokens: 400,
      effort: 'low',
      timeoutMs: 45_000,
    })
    const j = reply.isAnswered ? parseJudgement(reply.text) : null
    if (j) verdicts.push(...judgedVerdicts(j, recent.map(r => r.version)))
    else note = `judge unavailable (${reply.isAnswered ? 'unreadable reply' : reply.reason})`
  }
  return { experiment: name, review: newest.version, verdicts, note }
}

const ago = (ms: number) => {
  const min = Math.round(ms / 60_000)
  return min < 1 ? 'just now' : min < 60 ? `${min} min ago` : `${Math.round(min / 60)} h ago`
}

const refresh = async ($: $, root: string) => {
  const name = await read($, active)
  const next: Summary | null = name ? await scan($, root, name) : null
  const prev = await read($, summary)
  if (JSON.stringify(next) !== JSON.stringify(prev)) await update($, summary, () => next)
  const start = await read($, startedMs)
  const min = Math.round(((await $.clock.now()) - start) / 60_000)
  if (min !== (await read($, minutes))) await update($, minutes, () => min)
}

// The newest review as a key; a new key is a review the guard has not seen.
const newestReviewKey = async ($: $, root: string, name: string) => {
  const { reviews } = await readReviews($, experimentDir(root, name))
  const r = reviews[reviews.length - 1]
  return r ? `${r.file}@${r.mtimeMs}` : ''
}

// Switching to an experiment marks its current review as seen: the guard
// speaks only about reviews that land this session.
const activate = async ($: $, root: string, name: string, pin: boolean) => {
  const key = await newestReviewKey($, root, name)
  await update($, checked, c => (name in c ? c : { ...c, [name]: key }))
  await update($, active, () => name)
  await update($, isPinned, () => pin)
  await refresh($, root)
}

export const register: Register = on => {
  // Set at session.start; every hook passes through outside blender-lab.
  let root = ''

  on('session.start', async ($, e, next) => {
    const ran = await next(e)
    root = await $.session.root()
    const isLab =
      (await $.fs.exists(`${root}/tools/blender.sh`).catch(() => false)) &&
      (await $.fs.exists(`${root}/experiments`).catch(() => false))
    if (!isLab) {
      root = ''
      return ran
    }
    if ((await read($, startedMs)) === 0) {
      const now = await $.clock.now()
      await update($, startedMs, () => now)
    }
    await $.command.register({
      name: 'lab',
      description: 'Open the lab pane; /lab <experiment> pins one, /lab auto follows the work',
      argumentHint: '[experiment | auto]',
    })
    if ((await read($, active)) === null) {
      const name = await newestExperiment($, root)
      if (name) await activate($, root, name, false)
    }
    $.clock.every(5000, () => void refresh($, root).catch(() => undefined))
    void $.ui.open({ id: PANE, title: TITLE })
    return ran
  })

  on('command.run', { command: 'lab' }, async ($, e) => {
    if (!root) return { text: 'lab-watch only runs in blender-lab.' }
    const arg = e.args.trim()
    if (arg === 'auto') {
      await update($, isPinned, () => false)
    } else if (arg) {
      if (!(await isExperiment($, root, arg))) return { text: `No experiment named ${arg}.` }
      await activate($, root, arg, true)
    }
    await $.ui.open({ id: PANE, title: TITLE })
    const name = await read($, active)
    const pinned = await read($, isPinned)
    return { text: `Lab pane open on ${name ?? 'no experiment'}${pinned ? ' (pinned)' : ''}.` }
  })

  on('tool.call', async ($, e, next) => {
    if (!root || e.agentId) return next(e)
    const input = e as unknown as Record<string, unknown>
    const touched = experimentOf(e.tool, input)
    const ran = await next(e)

    if (e.tool === 'Bash' && isBlenderRun(e.command)) await update($, runs, n => n + 1)
    if (touched && touched !== (await read($, active)) && !(await read($, isPinned))) {
      if (await isExperiment($, root, touched)) await activate($, root, touched, false)
    }

    // The stall guard: after any main-loop call, look for a review it has not judged.
    const name = await read($, active)
    if (!name || ran.deny !== undefined) return ran
    const key = await newestReviewKey($, root, name)
    const seen = (await read($, checked))[name]
    if (!key || key === seen) return ran
    await update($, checked, c => ({ ...c, [name]: key }))
    const result: GuardResult | null = await judge($, root, name)
    if (!result) return ran
    await update($, guard, () => result)
    void refresh($, root).catch(() => undefined)
    if (result.verdicts.length === 0) return ran
    $.ui.toast(`Stall guard, ${name} ${result.review}: ${result.verdicts.map(v => v.rule).join(', ')}`, {
      timeoutMs: 8000,
    })
    return {
      ...ran,
      context: [...(ran.context ?? []), guardMessage(name, result.review, result.verdicts)],
    }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const s = await read($, summary)
    if (!root || !s) {
      return (
        <Box flexDirection="column">
          <Text dimColor>No experiment yet. /lab &lt;name&gt; picks one.</Text>
        </Box>
      )
    }
    const g = await read($, guard)
    const pinned = await read($, isPinned)
    const width = Math.max(20, e.props.bodyColumns)
    const now = await $.clock.now()
    const scores = s.scores.map(x => x.score)
    const real = s.scores.filter(x => x.score !== null)
    const best = real.reduce<(typeof real)[number] | null>(
      (b, x) => (b === null || (x.score ?? 0) > (b.score ?? 0) ? x : b),
      null,
    )
    const first = real[0]?.score
    const last = real[real.length - 1]?.score
    const ownGuard = g && g.experiment === s.name ? g : null

    let picture = null
    if (s.render && e.surface === 'terminal') {
      const { Image } = $.ui.resolve(e)
      const columns = Math.min(width, 64)
      const rows = Math.max(4, Math.min(24, Math.round((columns * s.render.height) / s.render.width / 2)))
      picture = (
        <Image
          key="render"
          source={{ file: s.render.path, format: 'png', generation: Math.round(s.render.mtimeMs) }}
          columns={columns}
          rows={rows}
          alt={`[${s.render.file}]`}
        />
      )
    }

    return (
      <Box flexDirection="column">
        <Text bold>
          {s.name}
          {pinned ? <Text dimColor> (pinned)</Text> : null}
        </Text>
        <Text>
          {s.step}
          {s.target !== null ? <Text dimColor> · target {s.target}</Text> : null}
          {s.isForked ? <Text dimColor> · forked</Text> : null}
        </Text>
        <Text> </Text>
        {picture}
        {s.render ? (
          <Text dimColor>
            {s.render.file} · {ago(now - s.render.mtimeMs)}
          </Text>
        ) : (
          <Text dimColor>No version render yet.</Text>
        )}
        <Text> </Text>
        <Text>
          <Text dimColor>Scores </Text>
          {real.length > 0 ? (
            <Text>
              <Text color="cyan">{sparkline(scores)}</Text> {first} → {last}
              <Text dimColor>
                {' '}
                · best {best?.score} ({best?.version})
              </Text>
            </Text>
          ) : (
            <Text dimColor>none yet</Text>
          )}
        </Text>
        <Text>
          <Text dimColor>Budget </Text>
          <Text color={s.reviewCount >= s.budget ? 'yellow' : undefined}>{bar(s.reviewCount, s.budget)}</Text> {s.reviewCount}/
          {s.budget} reviews
        </Text>
        <Text>
          <Text dimColor>Session </Text>
          {await read($, runs)} Blender runs · {await read($, minutes)} min
        </Text>
        <Text> </Text>
        {ownGuard === null ? (
          <Text dimColor>Guard: waiting for this session's first review</Text>
        ) : ownGuard.verdicts.length === 0 ? (
          <Text dimColor>
            Guard: no rule tripped after {ownGuard.review}
            {ownGuard.note ? ` (${ownGuard.note})` : ''}
          </Text>
        ) : (
          <Box flexDirection="column">
            <Text color="yellow" bold>
              Guard after {ownGuard.review}:
            </Text>
            {ownGuard.verdicts.map(v => (
              <Text color="yellow" wrap="wrap">
                • {v.text}
              </Text>
            ))}
          </Box>
        )}
      </Box>
    )
  })
}
