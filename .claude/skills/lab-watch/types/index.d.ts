export type ReviewScore = { version: string; score: number | null }

export type RenderInfo = {
  file: string
  path: string
  mtimeMs: number
  width: number
  height: number
}

export type Summary = {
  name: string
  step: string
  scores: ReviewScore[]
  reviewCount: number
  budget: number
  target: number | null
  isForked: boolean
  render: RenderInfo | null
}

export type VerdictRule = 'budget' | 'slope' | 'whole-form' | 'target' | 'repeat'

export type Verdict = { rule: VerdictRule; text: string }

export type GuardResult = {
  experiment: string
  review: string
  verdicts: Verdict[]
  note: string | null
}

declare module 'claude-code' {
  interface PluginState {
    'lab-watch': {
      active: string | null
      isPinned: boolean
      summary: Summary | null
      runs: number
      startedMs: number
      minutes: number
      guard: GuardResult | null
      checked: Record<string, string>
    }
  }
}
