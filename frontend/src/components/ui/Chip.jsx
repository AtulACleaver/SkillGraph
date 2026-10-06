import { Check, X } from 'lucide-react';

/** Removable skill chip used in the input. */
export default function Chip({ name, unrecognized = false, onRemove }) {
  return (
    <li
      className={`flex min-h-11 max-w-full items-stretch rounded-[10px] border bg-accent-tint text-accent-ink ${
        unrecognized ? 'border-dashed border-accent-line' : 'border-solid border-accent-line'
      }`}
    >
      <span
        title={name}
        className="flex min-w-0 max-w-[200px] sm:max-w-[260px] flex-col justify-center py-1.5 pl-3 pr-0.5"
      >
        <span className="truncate text-sm font-semibold leading-tight">{name}</span>
        {unrecognized && <span className="text-[11px] text-ink-3">Not in our list</span>}
      </span>
      <button
        type="button"
        onClick={onRemove}
        aria-label={`Remove ${name}`}
        className="grid size-11 flex-none place-items-center rounded-r-[10px] text-accent-ink hover:bg-accent-track focus-visible:outline-2"
      >
        <X size={15} strokeWidth={2.2} aria-hidden="true" />
      </button>
    </li>
  );
}

/** Static chip for skills the student already covers (result view). */
export function CoveredChip({ name }) {
  return (
    <li className="flex min-h-11 items-center gap-[7px] border border-line-2 bg-surface px-3 py-[7px] text-sm">
      <Check size={13} strokeWidth={3} className="flex-none text-accent" aria-hidden="true" />
      <span title={name} className="max-w-[240px] truncate">{name}</span>
    </li>
  );
}
