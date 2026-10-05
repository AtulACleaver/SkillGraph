import { Check } from 'lucide-react';
import Card from './Card';
import StepHeading from './StepHeading';

/** Panel 04: what the chosen role usually asks for (from GET /roles top_skills). */
export default function RoleSkillMix({ role, covered = [] }) {
  if (!role) return null;
  const have = new Set(covered);
  return (
    <Card tone="mix" className="mt-4" aria-labelledby="mix-heading">
      <StepHeading n="04" id="mix-heading" className="mb-6">
        What does this role usually ask for?
      </StepHeading>
      <div className="flex flex-wrap items-end justify-between gap-x-6 gap-y-3 border-b border-line pb-5">
        <div>
          <p className="text-[clamp(24px,4.6vw,30px)] font-bold leading-[1.15] tracking-[-0.035em]">{role.role_family}</p>
          <p className="mt-1.5 text-[15px] text-ink-3">{role.n_postings.toLocaleString('en-IN')} postings in the SkillGraph sample</p>
        </div>
        <span className="border-l-[3px] border-accent bg-accent-tint px-3.5 py-2 text-xs font-bold uppercase tracking-[0.12em] text-accent-ink">
          Core skill mix
        </span>
      </div>
      <ol className="grid grid-cols-1 gap-x-12 md:grid-cols-2">
        {role.top_skills.map((skill, i) => {
          const ok = have.has(skill);
          return (
            <li key={skill} className="flex items-center gap-3 border-b border-line py-3.5">
              <span className="w-[22px] text-[13px] tabular-nums text-ink-3">{String(i + 1).padStart(2, '0')}</span>
              <span className={`min-w-0 flex-1 text-base [overflow-wrap:anywhere] ${ok ? 'font-semibold' : ''}`}>{skill}</span>
              <span className={`flex items-center gap-[5px] whitespace-nowrap text-[13px] ${ok ? 'font-semibold text-accent-ink' : 'text-ink-3'}`}>
                {ok && <Check size={12} strokeWidth={3} aria-hidden="true" />}
                {ok ? 'You have this' : 'To learn'}
              </span>
            </li>
          );
        })}
      </ol>
    </Card>
  );
}
