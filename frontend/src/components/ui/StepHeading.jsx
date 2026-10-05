export function StepNumber({ n }) {
  return (
    <span
      aria-hidden="true"
      className="grid size-[30px] flex-none place-items-center rounded-full border-[1.5px] border-accent-line text-xs font-bold tracking-normal text-accent-ink"
    >
      {n}
    </span>
  );
}

export default function StepHeading({ as: Tag = 'h2', n, className = '', children, ...rest }) {
  return (
    <Tag className={`flex items-center gap-3 text-[13px] font-bold uppercase tracking-[0.12em] text-ink-2 ${className}`} {...rest}>
      <StepNumber n={n} />
      <span className="min-w-0">{children}</span>
    </Tag>
  );
}
