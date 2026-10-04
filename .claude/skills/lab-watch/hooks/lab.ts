// Pure parsing and the review-render rules. No `$` here, so tests run it directly.
import type { ReviewScore, Verdict } from '../types'

export type ReviewFile = { file: string; version: string; num: number; letter: string }

// review_v06.md, review_v07b.md. Preset reviews (review_v03_sunset.md) score another
// instrument, so they stay out of the trend, the same as old pre-pipeline names.
export const reviewFile = (file: string): ReviewFile | null => {
  const m = /^review_v(\d+)([a-z]?)\.md$/.exec(file)
  if (!m) return null
  return { file, version: `v${m[1]}${m[2]}`, num: Number(m[1]), letter: m[2] ?? '' }
}

export const byVersion = (a: ReviewFile, b: ReviewFile) =>
  a.num - b.num || a.letter.localeCompare(b.letter)

// Every review_v*.md, as tools/review_round.py counts them against the budget.
export const isAnyReview = (file: string) => /^review_v.*\.md$/.test(file)

// The first "N / 10" after the word Score: "**Score:** 6.3 / 10", "## 1. Score: 7.2 / 10".
export const parseScore = (text: string): number | null => {
  const m = /Score[^0-9\n]{0,16}?(\d+(?:\.\d+)?)\s*\/\s*10/i.exec(text)
  return m ? Number(m[1]) : null
}

// Same rule as tools/review_round.py: the first number under "## Budget", else 10.
export const parseBudget = (brief: string): number => {
  const m = /^##\s*Budget\s*\n+(.*)/m.exec(brief)
  const n = m?.[1] ? /\d+/.exec(m[1]) : null
  return n ? Number(n[0]) : 10
}

export const parseTarget = (brief: string): number | null => {
  const m = /^##\s*Target\s*\n+([\s\S]*?)(?=\n##\s|$)/m.exec(brief)
  const n = m?.[1] ? /Score\s+(\d+(?:\.\d+)?)/i.exec(m[1]) : null
  return n ? Number(n[1]) : null
}

// A long-running experiment works in rounds, each with its own reviewer brief: PROGRESS.md
// heads one "## Round three: the sofa (from v19)". Scores compare only within a round, so the
// rules read only the reviews from the newest round's first version on (all of them when none).
export const roundStart = (progress: string): number => {
  const all = [...progress.matchAll(/^##\s*Round\b[^\n]*\(from v(\d+)\)/gim)]
  const last = all[all.length - 1]
  return last ? Number(last[1]) : 0
}

// review-render logs "Fork: <old mechanism> → <new>" in PROGRESS.md.
export const isForked = (progress: string) => /Fork:\s*\S[^\n]*→/.test(progress)

export const hasResearch = (research: string, progress: string) =>
  (/^#+ *sources/im.test(research) && /https?:\/\//.test(research)) ||
  /research (step )?skipped/i.test(progress)

export const versionOf = (file: string) => /^(v\d+[a-z]?)/.exec(file)?.[1] ?? null

// A version render: v06.png, v06_sunset.png. Not crops, not raw EXRs.
export const isVersionRender = (file: string) =>
  /^v\d+.*\.png$/i.test(file) && !/crop/i.test(file)

const BARS = '▁▂▃▄▅▆▇█'

export const sparkline = (scores: readonly (number | null)[]): string => {
  const real = scores.filter((s): s is number => s !== null)
  if (real.length === 0) return ''
  const lo = Math.min(...real)
  const hi = Math.max(...real)
  return scores
    .map(s => (s === null ? ' ' : BARS[Math.round(((s - lo) / (hi - lo || 1)) * 7)]))
    .join('')
}

export const bar = (done: number, total: number, width = 10): string => {
  const filled = Math.min(width, Math.round((done / Math.max(1, total)) * width))
  return '█'.repeat(filled) + '░'.repeat(width - filled)
}

// The two rules that need no reading: budget spent and slope flat.
export const countedVerdicts = (args: {
  scores: readonly ReviewScore[]
  reviewCount: number
  budget: number
  isForked: boolean
}): Verdict[] => {
  const out: Verdict[] = []
  if (args.reviewCount >= args.budget) {
    out.push({
      rule: 'budget',
      text: `Budget spent: ${args.reviewCount} of ${args.budget} reviews. Stop the loop and calibrate (review-render, Stopping).`,
    })
  }
  // In a fork, only the budget and the taste rule stop the loop.
  const real = args.scores.map(s => s.score).filter((s): s is number => s !== null)
  if (!args.isForked && real.length >= 6) {
    const last = Math.max(...real.slice(-3))
    const before = Math.max(...real.slice(-6, -3))
    if (last < before + 0.3) {
      out.push({
        rule: 'slope',
        text: `Slope flat: the best of the last three rounds (${last}) does not beat the best of the three before (${before}) by 0.3. Stop and calibrate; fork once if the winner is more than 1.0 under the target.`,
      })
    }
  }
  return out
}

// The parts of a review the judge needs: the targets and the ranked problems.
export const excerpt = (text: string, limit = 1800): string => {
  const sections = text.split(/\n(?=##\s)/)
  const keep = sections.filter(s => /^##\s.*(target|problem|ranked)/i.test(s))
  const body = keep.length > 0 ? keep.join('\n') : text
  return body.length > limit ? `${body.slice(0, limit)}\n[…]` : body
}

export const JUDGE_SYSTEM =
  'You read art-direction reviews of 3D renders and answer only with one JSON object. No prose, no code fence.'

export const judgePrompt = (reviews: readonly { version: string; text: string }[]): string => {
  const blocks = reviews
    .map(r => `<review version="${r.version}">\n${excerpt(r.text)}\n</review>`)
    .join('\n\n')
  const newest = reviews[reviews.length - 1]?.version ?? ''
  return `Here are the last ${reviews.length} reviews of one experiment, oldest first. The newest is ${newest}.

${blocks}

Answer with this JSON object:
{
  "wholeFormWrong": boolean,   // true only if review ${newest} says the subject as a whole reads wrong: its overall form, shape or material ("barrels", "inflatable", "a bucket", "plastic", "a block model", "reads as CG"). A local defect is false.
  "wholeFormQuote": string,    // the words from ${newest} that say so, under 12 words; "" when false
  "missedEveryRound": string[], // the names of targets marked missed in EVERY review above (the same measurement, even when its numbers change), without the numbers; [] when fewer than 3 reviews
  "repeatedComplaint": string | null // when one of the top two ranked problems is the same underlying issue in EVERY review above, a label under 8 words; else null. null when fewer than 3 reviews
}`
}

export type Judgement = {
  wholeFormWrong: boolean
  wholeFormQuote: string
  missedEveryRound: string[]
  repeatedComplaint: string | null
}

export const parseJudgement = (text: string): Judgement | null => {
  const start = text.indexOf('{')
  const end = text.lastIndexOf('}')
  if (start < 0 || end <= start) return null
  try {
    const raw = JSON.parse(text.slice(start, end + 1)) as Record<string, unknown>
    return {
      wholeFormWrong: raw.wholeFormWrong === true,
      wholeFormQuote: typeof raw.wholeFormQuote === 'string' ? raw.wholeFormQuote : '',
      missedEveryRound: Array.isArray(raw.missedEveryRound)
        ? raw.missedEveryRound.filter((t): t is string => typeof t === 'string' && t.length > 0)
        : [],
      repeatedComplaint:
        typeof raw.repeatedComplaint === 'string' && raw.repeatedComplaint.length > 0
          ? raw.repeatedComplaint
          : null,
    }
  } catch {
    return null
  }
}

// The three rules that need the reviews read. `versions` are the reviews the judge saw.
export const judgedVerdicts = (j: Judgement, versions: readonly string[]): Verdict[] => {
  const out: Verdict[] = []
  const newest = versions[versions.length - 1] ?? ''
  const span = versions.length >= 3 ? `${versions[0]}–${newest}` : ''
  if (j.wholeFormWrong && versions.length >= 2) {
    const quote = j.wholeFormQuote ? ` ("${j.wholeFormQuote}")` : ''
    out.push({
      rule: 'whole-form',
      text: `Review ${newest} calls the whole form wrong${quote}. Consult the advisor (a model other than the builder) on the mechanism before the next round.`,
    })
  }
  if (versions.length >= 3 && j.missedEveryRound.length > 0) {
    out.push({
      rule: 'target',
      text: `Missed three rounds running (${span}): ${j.missedEveryRound.join('; ')}. If your changes aimed at it, consult the advisor before the next round.`,
    })
  }
  if (versions.length >= 3 && j.repeatedComplaint) {
    out.push({
      rule: 'repeat',
      text: `The same complaint ran three reviews (${span}): "${j.repeatedComplaint}". Stop tuning values: change the mechanism and run /research-reference for that effect.`,
    })
  }
  return out
}

export const guardMessage = (experiment: string, version: string, verdicts: readonly Verdict[]) =>
  [
    `lab-watch stall guard: review ${version} of ${experiment} trips these review-render rules.`,
    ...verdicts.map(v => `- ${v.text}`),
    'If you already acted on one, say so in PROGRESS.md and carry on.',
  ].join('\n')

// The experiment a tool call works on: a path under experiments/<name>/, or
// `review_round.py <name>`. Reads do not count, so loading another
// experiment's learnings does not switch the pane.
export const experimentOf = (tool: string, input: Record<string, unknown>): string | null => {
  const command = tool === 'Bash' ? String(input.command ?? '') : ''
  const text =
    tool === 'Bash'
      ? isLabRun(command) ? command : ''
      : tool === 'Write' || tool === 'Edit' || tool === 'NotebookEdit'
        ? String(input.file_path ?? input.notebook_path ?? '')
        : ''
  if (!text) return null
  const path = /experiments\/([A-Za-z0-9_.-]+)\//.exec(text)
  if (path?.[1]) return path[1]
  const round = /review_round\.py\s+([A-Za-z0-9_.-]+)/.exec(text)
  return round?.[1] && !round[1].startsWith('-') ? round[1] : null
}

// A command that runs Blender: tools/blender.sh or tools/sweep.sh in command
// position (after env assignments or `bash`), not a grep or cat that names them.
export const isBlenderRun = (command: string) =>
  /(^|[;&|(]\s*)(\w+=\S*\s+)*(bash\s+)?(\.\/)?tools\/(blender|sweep)\.sh\b/m.test(command)

// Any lab tool run: Blender, or a plain-python tool such as review_round.py.
export const isLabRun = (command: string) =>
  isBlenderRun(command) ||
  /(^|[;&|(]\s*)(\w+=\S*\s+)*python3?\s+(\.\/)?tools\/\w+\.py\b/m.test(command)
