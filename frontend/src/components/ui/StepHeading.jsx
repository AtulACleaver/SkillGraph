export function StepNumber({ n }) {
  return (
    <span
      aria-hidden="true"
      className="grid size-[38px] flex-none place-items-center rounded-full border-[2px] border-accent text-[15px] font-bold tracking-normal text-accent-ink"
    >
      {n}
    </span>
  );
}

export default function StepHeading({ as: Tag = 'h2', n, className = '', children, ...rest }) {
  return (
    <Tag className={`flex items-center gap-3 text-[14px] font-bold uppercase tracking-[1.5px] text-ink ${className}`} {...rest}>
      <StepNumber n={n} />
      <span className="min-w-0">{children}</span>
    </Tag>
  );
}
