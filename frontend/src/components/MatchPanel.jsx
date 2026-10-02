export default function MatchPanel({ matches = [], unrecognized = [], desiredRole = '', isLoading = false }) {
  if (isLoading) {
    return (
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <div className="h-5 w-48 bg-slate-800 rounded animate-pulse"></div>
          <div className="h-4 w-16 bg-slate-800 rounded animate-pulse"></div>
        </div>
        <div className="space-y-4 pt-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="space-y-2">
              <div className="flex justify-between">
                <div className="h-4 w-32 bg-slate-800 rounded animate-pulse"></div>
                <div className="h-4 w-10 bg-slate-800 rounded animate-pulse"></div>
              </div>
              <div className="h-3 w-full bg-slate-800/60 rounded-full animate-pulse"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Ensure top 3
  const topMatches = matches.slice(0, 3)

  return (
    <div className="bg-slate-900/80 border border-slate-800/90 backdrop-blur-xl rounded-2xl p-6 sm:p-7 shadow-xl space-y-5 transition-all">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 pb-1 border-b border-slate-800/60">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-teal-400 uppercase tracking-wider mb-1">
            <span className="w-1.5 h-1.5 rounded-full bg-teal-400"></span>
            Panel 3 · Model Predictions
          </div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-100">
            Roles That Actually Fit You
          </h2>
        </div>
        <span className="text-xs text-slate-400">
          Top 3 Market Alignments
        </span>
      </div>

      <p className="text-xs sm:text-sm text-slate-400">
        Calculated from mining thousands of active job requirements across the Indian tech sector.
      </p>

      {/* Matches List */}
      <div className="space-y-4 pt-1">
        {topMatches.length > 0 ? (
          topMatches.map((item, index) => {
            const roleName = item.role || item.role_family || 'Role'
            const probability = typeof item.probability === 'number'
              ? item.probability
              : parseFloat(item.probability || 0)
            
            // Format percentage (probability is 0..1 or 0..100)
            const pct = probability <= 1 ? Math.round(probability * 100) : Math.round(probability)
            const isPickedRole = desiredRole.trim().toLowerCase() === roleName.trim().toLowerCase()

            return (
              <div
                key={roleName}
                className={`p-4 rounded-xl border transition-all ${
                  isPickedRole
                    ? 'bg-emerald-500/10 border-emerald-500/40 shadow-lg shadow-emerald-950/20'
                    : 'bg-slate-950/40 border-slate-800/80 hover:border-slate-700/80'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2.5">
                    <span className="flex items-center justify-center w-6 h-6 rounded-full bg-slate-800 text-xs font-bold text-slate-300">
                      {index + 1}
                    </span>
                    <span className="text-sm sm:text-base font-semibold text-slate-100">
                      {roleName}
                    </span>
                    {isPickedRole && (
                      <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" />
                        </svg>
                        Your Target Role
                      </span>
                    )}
                  </div>
                  <span className="text-base sm:text-lg font-bold font-mono text-emerald-400">
                    {pct}%
                  </span>
                </div>

                {/* Horizontal Probability Bar */}
                <div className="w-full h-3 rounded-full bg-slate-800/80 overflow-hidden p-0.5">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ease-out ${
                      isPickedRole
                        ? 'bg-gradient-to-r from-emerald-400 to-teal-300 shadow-sm shadow-emerald-400/50'
                        : 'bg-gradient-to-r from-teal-500 to-cyan-400'
                    }`}
                    style={{ width: `${Math.min(Math.max(pct, 4), 100)}%` }}
                  ></div>
                </div>
              </div>
            )
          })
        ) : (
          <div className="text-center py-6 text-slate-500 text-sm">
            No matching role predictions available for this skillset.
          </div>
        )}
      </div>

      {/* Unrecognized Skills Quiet Line (Never silently drop them) */}
      {unrecognized && unrecognized.length > 0 && (
        <div className="pt-2 border-t border-slate-800/70">
          <div className="flex items-start gap-2 text-xs text-slate-400 bg-slate-950/40 px-3.5 py-2.5 rounded-xl border border-slate-800/60">
            <svg className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>
              <span className="text-slate-300 font-medium">We did not recognize: </span>
              <span className="text-slate-400 font-mono">
                {unrecognized.join(', ')}
              </span>
              <span className="text-slate-500 block text-[11px] mt-0.5">
                (These skills were not found in the current Indian market taxonomy)
              </span>
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
