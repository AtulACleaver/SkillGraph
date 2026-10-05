import { Scale } from 'lucide-react';
import Card from './ui/Card';
import StepHeading from './ui/StepHeading';
import ProbabilityBar from './ui/ProbabilityBar';
import { CoveredChip } from './ui/Chip';

const BANDS = {
  Ready: {
    index: 2,
    dot: 'border-band-ready bg-band-ready',
    fill: 'bg-band-ready',
    message: (role) => ['You’re ', 'ready', ` for most ${role} postings. Start applying, and keep building depth.`],
  },
  Close: {
    index: 1,
    dot: 'border-band-close bg-[linear-gradient(90deg,var(--color-band-close)_50%,transparent_50%)]',
    fill: 'bg-band-close',
    message: () => ['You’re ', 'within reach', '. One or two skills from the list below would likely move you into Ready.'],
  },
  'Not yet': {
    index: 0,
    dot: 'border-band-notyet bg-transparent',
    fill: 'bg-band-notyet',
    message: () => ['This is a ', 'starting point', ', not a verdict. The list below is the shortest path up — most students begin about here.'],
  },
};

const ZONES = [
  { label: 'Not yet', basis: 'flex-[0_0_40%]' },
  { label: 'Close · 40', basis: 'flex-[0_0_30%]' },
  { label: 'Ready · 70', basis: 'flex-[0_0_30%]' },
];

function getTension({ probability, coverage }) {
  let probBand = 'Not yet';
  if (probability >= 0.6) probBand = 'Ready';
  else if (probability >= 0.3) probBand = 'Close';

  let covBand = 'Not yet';
  if (coverage >= 0.2) covBand = 'Ready';
  else if (coverage >= 0.1) covBand = 'Close';

  const levels = { 'Ready': 3, 'Close': 2, 'Not yet': 1 };
  
  let tension = null;
  if (probBand !== covBand) {
    if (levels[probBand] > levels[covBand]) {
      tension = {
        title: 'Coverage held it back',
        text: `Probability alone would be ${probBand}, but coverage held it back.`,
      };
    } else {
      tension = {
        title: 'Probability held it back',
        text: `Coverage alone would be ${covBand}, but probability held it back.`,
      };
    }
  }
  
  const finalBandStr = levels[probBand] < levels[covBand] ? probBand : covBand;
  return { finalBandStr, tension };
}

export default function ReadinessPanel({ readiness, role }) {
  const probability = Math.max(0, Math.min(1, readiness.probability ?? 0));
  const pct = Math.round(probability * 100);
  const covered = readiness.covered || [];
  const have = covered.length;
  const total = have + (readiness.missing_count ?? 0);
  const coverage = readiness.coverage ?? (total ? have / total : 0);
  const coveragePct = Math.round(coverage * 100);
  
  const { finalBandStr, tension } = getTension({ probability, coverage });
  const band = BANDS[finalBandStr] || BANDS['Not yet'];
  
  const [msgA, msgB, msgC] = band.message(role);

  return (
    <Card tone="readiness" aria-labelledby="readiness-heading">
      <StepHeading n="01" id="readiness-heading" className="mb-6">
        Am I ready for {role}?
      </StepHeading>

      <div className="flex flex-wrap items-end justify-between gap-x-10 gap-y-6">
        <div className="flex-[0_1_auto]">
          <p className="text-[clamp(88px,23vw,156px)] font-bold leading-[0.86] tracking-[-0.06em] tabular-nums">
            {pct}
            <span className="tracking-[-0.04em]">%</span>
            <span className="sr-only"> readiness</span>
          </p>
          <p className="mt-4 flex items-center gap-[9px] text-lg font-bold">
            <span aria-hidden="true" className={`size-3 flex-none rounded-full border-[2.5px] ${band.dot}`} />
            <span>
              <span className="sr-only">Band: </span>
              {readiness.band}
            </span>
            <span aria-hidden="true" className="text-[15px] font-normal text-ink-3">
              · readiness band
            </span>
          </p>
        </div>

        <div className="max-w-[400px] flex-[1_1_280px]">
          <p className="mb-5 text-base leading-[1.6] text-ink-2 text-pretty">
            {msgA}
            <strong className="font-bold text-ink">{msgB}</strong>
            {msgC}
          </p>
          <div aria-hidden="true">
            <div className="relative h-2 bg-line-2">
              <div className={`absolute inset-y-0 left-0 ${band.fill}`} style={{ width: `${pct}%` }} />
              <span className="absolute bottom-[-3px] left-[40%] top-[-3px] w-[3px] bg-tint" />
              <span className="absolute bottom-[-3px] left-[70%] top-[-3px] w-[3px] bg-tint" />
            </div>
            <div className="mt-2 flex text-xs">
              {ZONES.map((z, i) => (
                <span key={z.label} className={`${z.basis} ${i === band.index ? 'font-bold text-ink' : 'text-ink-3'}`}>
                  {z.label}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 border-t border-line-2 pt-7">
        <div className="mb-3.5 flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1.5">
          <div className="flex flex-wrap items-baseline gap-x-2.5 gap-y-1">
            <span className="flex-none whitespace-nowrap text-[clamp(36px,7vw,48px)] font-bold leading-none tracking-[-0.045em] tabular-nums">
              {have}
              <span className="font-medium text-ink-3">&nbsp;of&nbsp;{total}</span>
            </span>
            <span className="text-[15px] text-ink-2">core skills covered</span>
          </div>
          <span className="text-[15px] font-semibold tabular-nums text-accent-ink">{coveragePct}% coverage</span>
        </div>
        <ProbabilityBar value={coverage} size="h-2" track="bg-accent-track" fill="bg-accent" />
        <p className="mb-3 mt-3.5 text-[15px] text-ink-2">
          covers {have} of {total} top skills
        </p>

        {have > 0 ? (
          <ul aria-label="Skills you have that this role asks for" className="flex flex-wrap gap-2">
            {covered.map((s) => (
              <CoveredChip key={s} name={s} />
            ))}
          </ul>
        ) : (
          <p className="border border-dashed border-line-2 px-3.5 py-3 text-sm text-ink-2">
            None of your skills are on this role's usual list yet. That's exactly what section 02 is for.
          </p>
        )}

        {tension && (
          <div className="mt-6 grid grid-cols-[auto_minmax(0,1fr)] gap-3.5 border border-line-2 bg-surface px-5 py-[18px]">
            <Scale size={20} strokeWidth={2} className="mt-px text-ink-2" aria-hidden="true" />
            <div>
              <p className="mb-1 text-base font-bold">{tension.title}</p>
              <p className="max-w-[72ch] text-sm leading-[1.6] text-ink-2 text-pretty">{tension.text}</p>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
