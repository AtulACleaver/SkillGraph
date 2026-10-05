import { ArrowRight, Check } from 'lucide-react';
import Card from './ui/Card';
import StepHeading from './ui/StepHeading';
import ProbabilityBar from './ui/ProbabilityBar';

const formatPct = (p) => (p < 0.01 ? '<1%' : `${Math.round(p * 100)}%`);

export default function MatchPanel({ matches = [], desiredRole, onSwitchRole, className = '' }) {
  const top = matches.slice(0, 3);
  const chosenInTop = top.some((m) => m.role === desiredRole);
  const best = top[0]?.role;
  const notTopMatch = best && best !== desiredRole;

  return (
    <Card tone="fit" className={className} aria-labelledby="match-heading">
      <StepHeading n="03" id="match-heading" className="mb-[18px]">
        Which roles fit me right now?
      </StepHeading>

      {notTopMatch && (
        <div className="mb-1.5 border border-fit bg-fit-tint px-[18px] pb-5 pt-[18px]">
          <p className="mb-1.5 text-xs font-bold uppercase tracking-[0.14em] text-fit-ink">Worth knowing</p>
          <p className="mb-2 text-[clamp(18px,3.4vw,21px)] font-bold leading-[1.25] tracking-[-0.02em] text-balance">
            Best fit is {best}.
          </p>
          <p className="mb-4 text-sm leading-[1.55] text-ink-2 text-pretty">
            Not a dead end. It shows where you'd be competitive today. Section 02 shows what {desiredRole} would take.
          </p>
          {onSwitchRole && (
            <button
              type="button"
              onClick={() => onSwitchRole(best)}
              className="inline-flex min-h-11 items-center gap-2 border border-fit bg-surface px-3.5 text-left text-sm font-semibold text-fit-ink hover:bg-bg"
            >
              <span>Check readiness for {best}</span>
              <ArrowRight size={15} strokeWidth={2.2} className="flex-none" aria-hidden="true" />
            </button>
          )}
        </div>
      )}

      {chosenInTop && (
        <p className="mb-1.5 border-l-[3px] border-fit bg-fit-tint px-4 py-3 text-sm leading-normal text-fit-ink">
          Model probability for each role family, given your skills.
        </p>
      )}

      {top.length > 0 ? (
        <>
          <ol>
            {top.map((m, i) => {
              const isPick = m.role === desiredRole;
              return (
                <li key={m.role} className="grid grid-cols-[24px_minmax(0,1fr)] gap-x-2.5 border-b border-line py-5">
                  <span className="pt-1 text-sm tabular-nums text-fit-ink">{i + 1}</span>
                  <div className="min-w-0">
                    <div className="flex items-baseline justify-between gap-3">
                      <span className="flex min-w-0 flex-wrap items-center gap-x-2.5 gap-y-1 text-[17px] font-semibold">
                        <span className="[overflow-wrap:anywhere]">{m.role}</span>
                        {isPick && (
                          <span className="inline-flex items-center gap-1 bg-accent-tint px-[7px] py-0.5 text-[11px] font-bold uppercase tracking-[0.08em] text-accent-ink">
                            <Check size={10} strokeWidth={3.5} aria-hidden="true" />
                            Your pick
                          </span>
                        )}
                      </span>
                      <span className="text-[28px] font-bold leading-none tracking-[-0.03em] tabular-nums text-fit">{formatPct(m.probability)}</span>
                    </div>
                    <ProbabilityBar value={m.probability} minPercent={0.6} size="h-[5px]" track="bg-fit-track" fill="bg-fit" className="mt-3.5" />
                  </div>
                </li>
              );
            })}
            {(!chosenInTop && desiredRole) && (
              <li className="grid grid-cols-[24px_minmax(0,1fr)] gap-x-2.5 pb-1 pt-4">
                <span aria-hidden="true" className="pt-px text-sm text-ink-3">
                  -
                </span>
                <div className="flex flex-wrap justify-between gap-x-3 gap-y-1 text-[15px]">
                  <span className="text-ink-2">
                    <span className="text-ink-3">Your pick: </span>
                    {desiredRole}
                  </span>
                  <span className="text-ink-3">Not in top 3</span>
                </div>
              </li>
            )}
          </ol>
          <p className="mt-4 text-[13px] leading-normal text-ink-3">Fit compares role families with each other, so it can differ from your readiness score.</p>
        </>
      ) : (
        <p className="text-[15px] leading-[1.55] text-ink-2">
          We couldn't match your skills to a role family yet. Add a few skills we recognise and try again.
        </p>
      )}
    </Card>
  );
}
