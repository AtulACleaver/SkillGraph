/** Decorative bar. The number it represents must always be printed as text nearby. */
export default function ProbabilityBar({ value = 0, size = 'h-2', track = 'bg-accent-track', fill = 'bg-accent', minPercent = 0, className = '' }) {
  const pct = Math.max(minPercent, Math.min(100, value * 100));
  return (
    <div aria-hidden="true" className={`${size} ${track} ${className}`}>
      <div className={`h-full ${fill}`} style={{ width: `${pct}%` }} />
    </div>
  );
}
