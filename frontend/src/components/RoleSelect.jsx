import { StepNumber } from './ui/StepHeading';
import { SkeletonRoleRow } from './ui/Skeleton';

const SKELETON_WIDTHS = [
  ['62%', '48%'],
  ['70%', '56%'],
  ['58%', '52%'],
  ['52%', '60%'],
  ['64%', '46%'],
  ['56%', '50%'],
];

export default function RoleSelect({ roles, status, value, onChange, selectedNames = [], name = 'desired-role' }) {
  const have = new Set(selectedNames);
  const ready = status === 'ready';

  return (
    <section className="min-w-0">
      <fieldset className="m-0 min-w-0 border-0 p-0" aria-busy={!ready}>
        <legend className="mb-5 flex items-center gap-3 p-0 text-[13px] font-bold uppercase tracking-[0.12em] text-ink-2">
          <StepNumber n="02" />
          Role you're aiming for
        </legend>

        <div className="border-t border-line-2">
          {!ready && (
            <>
              <span className="sr-only">{status === 'error' ? 'Roles could not be loaded.' : 'Loading roles…'}</span>
              {SKELETON_WIDTHS.map(([a, b], i) => (
                <SkeletonRoleRow key={i} w1={a} w2={b} />
              ))}
            </>
          )}

          {ready && roles.length === 0 && (
            <p className="border-b border-line py-5 text-[15px] text-ink-2">No roles are available right now. Please try again in a moment.</p>
          )}

          {ready &&
            roles.map((role) => {
              const checked = role.role_family === value;
              const hits = role.top_skills.filter((s) => have.has(s)).length;
              return (
                <label
                  key={role.role_family}
                  className={`flex cursor-pointer items-center gap-4 border-b border-line py-4 pr-3 transition-colors ${
                    checked ? 'bg-accent-tint pl-4 shadow-[inset_3px_0_0_var(--color-accent)]' : 'pl-0 hover:bg-tint'
                  }`}
                >
                  <span className="min-w-0 flex-1">
                    <span className="block text-[17px] font-semibold tracking-[-0.01em]">{role.role_family}</span>
                    <span className="mt-[3px] block text-[13px] text-ink-3 [overflow-wrap:anywhere]">
                      {role.n_postings.toLocaleString('en-IN')} postings · {role.top_skills.slice(0, 3).join(' · ')}
                    </span>
                    {checked && (
                      <span className="mt-2 block text-[13px] font-medium text-accent-ink">
                        {selectedNames.length
                          ? `You have ${hits} of the ${role.top_skills.length} skills it usually asks for.`
                          : `Usually asks for ${role.top_skills.length} core skills.`}
                      </span>
                    )}
                  </span>
                  <input
                    type="radio"
                    name={name}
                    value={role.role_family}
                    checked={checked}
                    onChange={() => onChange(role.role_family)}
                    className="m-0 size-[22px] flex-none cursor-pointer accent-accent"
                  />
                </label>
              );
            })}
        </div>
      </fieldset>
    </section>
  );
}
