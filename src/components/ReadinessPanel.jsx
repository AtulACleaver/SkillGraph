export default function ReadinessPanel({ desiredRole = 'Target Role', selectedSkills = [] }) {
  return (
    <div className="bg-slate-900/80 border border-slate-800/90 backdrop-blur-xl rounded-2xl p-6 sm:p-7 shadow-xl space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 pb-1 border-b border-slate-800/60">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            Panel 1 · Readiness Score
          </div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-100">
            Readiness for {desiredRole}
          </h2>
        </div>
        <span className="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-400 font-mono">
          Day 5 Sprint Target
        </span>
      </div>

      <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800/80 flex items-center justify-between">
        <div>
          <div className="text-xs text-slate-400">Target Role Evaluated</div>
          <div className="text-base font-semibold text-slate-200 mt-0.5">{desiredRole}</div>
          <div className="text-xs text-slate-500 mt-1">
            {selectedSkills.length} skill{selectedSkills.length === 1 ? '' : 's'} submitted
          </div>
        </div>
        <div className="text-right">
          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
            Wiring /readiness on Day 5
          </span>
        </div>
      </div>
    </div>
  )
}
