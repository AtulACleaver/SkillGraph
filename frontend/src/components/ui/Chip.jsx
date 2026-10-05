import { Check, X } from 'lucide-react';

/** Removable skill chip used in the input. */
export default function Chip({ name, unrecognized = false, onRemove }) {
  return (
    <li className={`flex min-h-11 max-w-full items-stretch border bg-surface ${unrecognized ? 'border-dashed' : 'border-solid'} border-line-2`}>
      <span className="flex min-w-0 flex-col justify-center py-1.5 pl-3 pr-0.5">
        <span className="text-sm font-semibold leading-tight [overflow-wrap:anywhere]">{name}</span>
        {unrecognized && <span className="text-[11px] text-ink-3">Not in our list</span>}
      </span>
      <button
        type="button"
        onClick={onRemove}
        aria-label={`Remove ${name}`}
        className="grid w-10 flex-none place-items-center text-ink-2 hover:bg-tint hover:text-ink"
      >
        <X size={15} strokeWidth={2.2} aria-hidden="true" />
      </button>
    </li>
  );
}

/** Static chip for skills the student already covers (result view). */
export function CoveredChip({ name }) {
  return (
    <li className="flex items-center gap-[7px] border border-line-2 bg-surface px-3 py-[7px] text-sm">
      <Check size={13} strokeWidth={3} className="flex-none text-accent" aria-hidden="true" />
      <span className="[overflow-wrap:anywhere]">{name}</span>
    </li>
  );
}
