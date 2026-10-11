import { useReveal } from '../../hooks/useReveal';

export function StepNumber({ n }) {
  const [ref, isRevealed] = useReveal({ threshold: 0 });
  return (
    <span
      ref={ref}
      aria-hidden="true"
      className={`grid size-[38px] flex-none place-items-center rounded-full border-[2px] border-accent text-[15px] font-bold tracking-normal text-accent-ink transition-all duration-500 ease-out ${isRevealed ? 'opacity-100 scale-100' : 'opacity-0 scale-75'}`}
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
