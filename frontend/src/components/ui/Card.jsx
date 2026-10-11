import { forwardRef } from 'react';

const TONES = {
  readiness: 'border-t-4 border-t-accent bg-tint p-[clamp(20px,4.5vw,40px)]',
  plain: 'bg-surface p-[clamp(20px,4.5vw,36px)]',
  fit: 'border-t-4 border-t-fit bg-surface p-[clamp(20px,4.5vw,36px)]',
  mix: 'border-t-4 border-t-accent bg-surface p-[clamp(20px,4.5vw,36px)]',
  error: 'border-t-4 border-t-ink-3 bg-surface p-[clamp(20px,4vw,32px)]',
  status: 'border-t-4 border-t-accent bg-tint p-[clamp(20px,4vw,32px)]',
  notice: 'border-t-[3px] border-t-ink-3 bg-tint px-[clamp(18px,4vw,28px)] py-[22px]',
};

const Card = forwardRef(function Card({ as: Tag = 'section', tone = 'plain', shadow = true, className = '', children, ...rest }, ref) {
  return (
    <Tag ref={ref} className={`min-w-0 border border-line ${TONES[tone] || TONES.plain} ${shadow ? 'shadow-card' : ''} ${className}`} {...rest}>
      {children}
    </Tag>
  );
});

Card.displayName = 'Card';

export default Card;
