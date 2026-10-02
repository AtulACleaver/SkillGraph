export default function ReadinessPanel({
  desiredRole = 'Target Role',
  readinessData = null,
  isLoading = false
}) {
  if (isLoading) {
    return (
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-7 shadow-xl space-y-5 animate-pulse">
        <div className="flex justify-between items-center pb-2 border-b border-slate-800/60">
          <div className="space-y-2">
            <div className="h-4 w-32 bg-slate-800 rounded"></div>
            <div className="h-6 w-48 bg-slate-800 rounded"></div>
          </div>
          <div className="h-8 w-24 bg-slate-800 rounded-full"></div>
        </div>
        <div className="h-20 bg-slate-800/50 rounded-xl"></div>
        <div className="h-12 bg-slate-800/40 rounded-xl"></div>
      </div>
    )
  }

  // Safe defaults if readinessData is not yet populated
  const data = readinessData || {
    probability: 0.48,
    band: 'Close',
    coverage: 0.35,
    covered: [],
    missing_count: 13
  }

  const prob = typeof data.probability === 'number'
    ? data.probability <= 1 ? Math.round(data.probability * 100) : Math.round(data.probability)
    : 48

  const band = data.band || (prob >= 70 ? 'Ready' : prob >= 45 ? 'Close' : 'Not yet')
  const coveredSkills = Array.isArray(data.covered) ? data.covered : []
  const missingCount = typeof data.missing_count === 'number' ? data.missing_count : 13
  const totalSkillsForRole = coveredSkills.length + missingCount || 20
  const coveragePct = Math.round((coveredSkills.length / Math.max(totalSkillsForRole, 1)) * 100)

  // Notion Rule: Green for Ready, Amber for Close, Grey for Not yet. Never Red.
  const bandStyles = {
    Ready: {
      badge: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
      pill: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
      text: 'text-emerald-400',
      bar: 'from-emerald-400 to-teal-300',
      summary: 'Strong match for standard job postings in this family.'
    },
    Close: {
      badge: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
      pill: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
      text: 'text-amber-400',
      bar: 'from-amber-400 to-amber-300',
      summary: 'Close to market threshold. A few key skills will bridge the gap.'
    },
    'Not yet': {
      badge: 'bg-slate-700/40 text-slate-300 border-slate-600/40',
      pill: 'bg-slate-800 text-slate-300 border-slate-700/60',
      text: 'text-slate-300',
      bar: 'from-slate-500 to-slate-400',
      summary: 'Significant skill overlap still required for this specific role family.'
    }
  }

  const currentBandStyle = bandStyles[band] || bandStyles['Not yet']

  // Detect signal divergence / tension between statistical model & keyword coverage
  // E.g. high coverage but low probability, or low coverage but high probability
  const hasHighCoverageLowProb = coveragePct >= 50 && prob < 45
  const hasLowCoverageHighProb = coveragePct <= 30 && prob >= 65
  const hasDivergence = hasHighCoverageLowProb || hasLowCoverageHighProb

  return (
    <div className="bg-slate-900/80 border border-slate-800/90 backdrop-blur-xl rounded-2xl p-6 sm:p-7 shadow-xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-800/60">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            Panel 1 · Readiness Score
          </div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-100">
            Readiness for {desiredRole}
          </h2>
        </div>

        {/* Band Label Badge (Green, Amber, or Grey - Never Red) */}
        <div className={`px-3.5 py-1.5 rounded-full border text-xs sm:text-sm font-bold flex items-center gap-1.5 self-start sm:self-auto ${currentBandStyle.badge}`}>
          <span className="w-2 h-2 rounded-full bg-current"></span>
          <span>{band}</span>
        </div>
      </div>

      {/* Main Metric Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-5 rounded-xl bg-slate-950/50 border border-slate-800/80 items-center">
        {/* Big Percentage & Band */}
        <div className="md:col-span-1 border-b md:border-b-0 md:border-r border-slate-800/70 pb-4 md:pb-0 md:pr-4">
          <div className="text-xs uppercase font-medium tracking-wider text-slate-400">
            Model Probability
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className={`text-5xl sm:text-6xl font-black font-mono tracking-tight ${currentBandStyle.text}`}>
              {prob}%
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Band classification: <strong className={currentBandStyle.text}>{band}</strong>
          </p>
        </div>

        {/* Coverage Summary & Visual Bars */}
        <div className="md:col-span-2 space-y-3 md:pl-2">
          <div>
            <div className="flex justify-between items-center text-xs mb-1.5">
              <span className="text-slate-300 font-medium">Market Skill Coverage</span>
              <span className="text-slate-400 font-mono font-semibold">{coveragePct}% ({coveredSkills.length}/{totalSkillsForRole})</span>
            </div>
            {/* Dual visual track */}
            <div className="w-full h-3 rounded-full bg-slate-800/80 overflow-hidden p-0.5">
              <div
                className={`h-full rounded-full bg-gradient-to-r ${currentBandStyle.bar} transition-all duration-700 ease-out`}
                style={{ width: `${Math.min(Math.max(coveragePct, 5), 100)}%` }}
              ></div>
            </div>
          </div>

          {/* Explicit Coverage Line per Notion spec */}
          <p className="text-xs sm:text-sm text-slate-300 font-normal">
            You have <strong className="text-white font-semibold">{coveredSkills.length}</strong> of the <strong className="text-white font-semibold">{totalSkillsForRole}</strong> skills this role usually asks for in Indian postings.
          </p>
        </div>
      </div>

      {/* Covered Skills Chips Section */}
      {coveredSkills.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" />
            </svg>
            Matching Skills You Possess ({coveredSkills.length})
          </div>
          <div className="flex flex-wrap gap-1.5">
            {coveredSkills.map(skill => (
              <span
                key={skill}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/20"
              >
                <span className="text-emerald-400 text-[10px]">✓</span>
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Signal Tension / Disagreement Callout (Per Notion Day 5 Concept) */}
      {hasDivergence && (
        <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-200 text-xs space-y-1">
          <div className="font-semibold flex items-center gap-1.5 text-amber-300">
            <svg className="w-4 h-4 text-amber-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            Signal Discrepancy Note
          </div>
          <p className="text-amber-200/90 leading-relaxed">
            {hasHighCoverageLowProb ? (
              <>
                You have significant keyword coverage ({coveragePct}%), but the predictive classifier band is <strong>{band}</strong> ({prob}%). This indicates you have peripheral tooling, but are missing critical high-weight anchor skills that recruiters prioritize for this title.
              </>
            ) : (
              <>
                Your raw coverage count is lower ({coveragePct}%), yet your predicted probability is high at <strong>{prob}% ({band})</strong>. This occurs because the specific skills you possess carry heavy predictive weight for this role family.
              </>
            )}
          </p>
        </div>
      )}
    </div>
  )
}
