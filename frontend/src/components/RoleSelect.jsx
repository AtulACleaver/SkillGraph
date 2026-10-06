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
        <legend className="mb-5 flex items-center gap-3 p-0 text-[14px] font-bold uppercase tracking-[1.5px] text-ink">
          <StepNumber n="02" />
          Role you're aiming for
        </legend>

        <div className="flex flex-col gap-3">
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
            roles.map((role, i) => {
              const checked = role.role_family === value;
              const hits = role.top_skills.filter((s) => have.has(s)).length;
              const roleInputId = `role-opt-${role.role_family.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;
              return (
                <label
                  key={role.role_family}
                  htmlFor={roleInputId}
                  className={`flex min-h-[72px] cursor-pointer items-center gap-4 rounded-xl border p-4 transition-all duration-300 hover:-translate-y-[1px] hover:border-accent hover:shadow-sm animate-fade-in-up opacity-0 [animation-fill-mode:both] ${
                    checked ? 'border-accent bg-accent-tint shadow-[0_2px_8px_-2px_rgba(23,128,79,0.15)]' : 'border-line bg-surface'
                  }`}
                  style={{ animationDelay: `${350 + i * 70}ms` }}
                >
                  <span className="min-w-0 flex-1">
                    <span className="block text-[17px] font-bold">{role.role_family}</span>
                    <span className="mt-1 block text-[14px] font-medium text-ink-3 [overflow-wrap:anywhere]">
                      {role.n_postings.toLocaleString('en-IN')} postings · {role.top_skills.slice(0, 3).join(' · ')}
                    </span>
                    {checked && (
                      <span className="mt-2 block text-[14px] font-semibold text-accent-ink">
                        {selectedNames.length
                          ? `You have ${hits} of the ${role.top_skills.length} skills it usually asks for.`
                          : `Usually asks for ${role.top_skills.length} core skills.`}
                      </span>
                    )}
                  </span>
                  <input
                    type="radio"
                    id={roleInputId}
                    name={name}
                    value={role.role_family}
                    checked={checked}
                    onChange={() => onChange(role.role_family)}
                    className="m-0 size-5 flex-none cursor-pointer accent-accent transition-all duration-300"
                  />
                </label>
              );
            })}
        </div>
      </fieldset>
    </section>
  );
}
