import { useReveal } from '../../hooks/useReveal';

/** Decorative bar. The number it represents must always be printed as text nearby. */
export default function ProbabilityBar({ value = 0, size = 'h-2', track = 'bg-accent-track', fill = 'bg-accent', minPercent = 0, className = '' }) {
  const [ref, isRevealed] = useReveal({ threshold: 0 });
  const pct = Math.max(minPercent, Math.min(100, value * 100));
  return (
    <div ref={ref} aria-hidden="true" className={`${size} ${track} overflow-hidden ${className}`}>
      <div className={`h-full ${fill} transition-[width] duration-1000 ease-out`} style={{ width: isRevealed ? `${pct}%` : '0%' }} />
    </div>
  );
}
