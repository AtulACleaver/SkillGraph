import { Check, Link as LinkIcon } from 'lucide-react';
import Card from './ui/Card';
import StepHeading from './ui/StepHeading';
import ProbabilityBar from './ui/ProbabilityBar';
import { useReveal } from '../hooks/useReveal';

// coverage_pct is a 0–1 share; tolerate a 0–100 value too.
const toShare = (v) => (v > 1 ? v / 100 : v || 0);

export default function GapPanel({ recommendations = [], probability = 0, role, className = '' }) {
  const before = Math.round(probability * 100);
  const recs = recommendations.slice(0, 5);
  const [ref, isRevealed] = useReveal({ threshold: 0.1 });

  return (
    <Card ref={ref} tone="plain" className={`${className} animate-fade-in-up`} aria-labelledby="gap-heading">
      <StepHeading n="02" id="gap-heading" className="mb-1.5">
        What should I learn next?
      </StepHeading>

      {recs.length > 0 ? (
        <>
          <p className="mb-[18px] ml-[42px] text-[13px] text-ink-3">Ranked by readiness gain weighted by how often the role asks for it.</p>
          <ol className="border-t border-line">
            {recs.map((rec, i) => {
              const after = Math.round(Math.min(1, probability + (rec.readiness_gain || 0)) * 100);
              const points = after - before;
              const share = toShare(rec.coverage_pct);
              const partners = Array.isArray(rec.learn_with) ? rec.learn_with : (rec.learn_with ? [rec.learn_with] : []);
              return (
                <li 
                  key={rec.skill} 
                  className={`grid grid-cols-[30px_minmax(0,1fr)] gap-x-3 border-b border-line pb-5 pt-[18px] transition-all duration-500 ease-out ${isRevealed ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-3'}`}
                  style={{ transitionDelay: `${i * 100}ms` }}
                >
                  <span className="pt-[3px] text-sm font-medium tabular-nums text-accent-ink">{String(i + 1).padStart(2, '0')}</span>
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
                      <span className="min-w-0 text-lg font-semibold tracking-[-0.01em] [overflow-wrap:anywhere]">{rec.skill}</span>
                      <span className="whitespace-nowrap text-[17px] tabular-nums text-ink-3">
                        readiness <strong className="font-bold text-ink">{before}% to {after}%</strong>
                      </span>
                    </div>

                    {partners.length > 0 && (
                      <div className="mt-2 flex flex-wrap items-center gap-1.5 text-[13px] text-ink-2">
                        <LinkIcon size={13} strokeWidth={2.2} className="flex-none text-accent" aria-hidden="true" />
                        <span className="mr-1">Learn alongside:</span>
                        {partners.map(p => (
                          <span key={p} className="inline-flex items-center rounded-sm bg-surface px-1.5 py-0.5 text-[11px] font-semibold border border-line-2">
                            {p}
                          </span>
                        ))}
                      </div>
                    )}

                    <div className="mt-3 flex justify-between gap-3 text-[13px]">
                      <span className="text-ink-3">
                        in {Math.round(share * 100)}% of {role} postings
                      </span>
                      <span className="whitespace-nowrap font-bold text-accent-ink">{points >= 1 ? `+${points} points` : '< 1 point'}</span>
                    </div>
                    <ProbabilityBar value={share} size="h-[5px]" track="bg-accent-track" fill="bg-accent" className="mt-2" />
                  </div>
                </li>
              );
            })}
          </ol>
        </>
      ) : (
        <div className="mt-[18px] grid grid-cols-[auto_minmax(0,1fr)] gap-3.5 border-t border-line pb-1 pt-5">
          <span aria-hidden="true" className="grid size-[30px] place-items-center rounded-full bg-accent text-white">
            <Check size={15} strokeWidth={3} />
          </span>
          <div>
            <p className="mb-1.5 text-lg font-bold tracking-[-0.015em]">You already have every skill this role commonly asks for.</p>
            <p className="max-w-[46ch] text-sm leading-[1.6] text-ink-2">
              From here, depth counts more than breadth. Projects and interview practice will move you further than another skill.
            </p>
          </div>
        </div>
      )}
    </Card>
  );
}
