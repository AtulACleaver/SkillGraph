export default function GapPanel({ desiredRole = 'Target Role' }) {
  return (
    <div className="bg-slate-900/80 border border-slate-800/90 backdrop-blur-xl rounded-2xl p-6 sm:p-7 shadow-xl space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 pb-1 border-b border-slate-800/60">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-1">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
            Panel 2 · Skill Gaps
          </div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-100">
            What to Learn Next
          </h2>
        </div>
        <span className="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-400 font-mono">
          Day 6 Sprint Target
        </span>
      </div>

      <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800/80 flex items-center justify-between">
        <div>
          <div className="text-xs text-slate-400">High-Impact Market Recommendations</div>
          <div className="text-base font-semibold text-slate-200 mt-0.5">Top 5 Curated Skill Gaps</div>
          <div className="text-xs text-slate-500 mt-1">
            Optimized for {desiredRole} career progression
          </div>
        </div>
        <div className="text-right">
          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
            Wiring /gap on Day 6
          </span>
        </div>
      </div>
    </div>
  )
}
