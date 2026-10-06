import { useEffect, useRef, useState } from 'react';
import { Search } from 'lucide-react';
import { searchSkills, isCancelled } from '../api/client';
import Chip from './ui/Chip';
import { StepNumber } from './ui/StepHeading';

const CHIP_LIMIT = 30;
const DEBOUNCE_MS = 200;

/**
 * value: [{ name: string, known: boolean }]
 * known = picked from /skills results; false = added as typed (shown dashed).
 */
export default function SkillInput({ value, onChange, inputId = 'skill-search' }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searchStatus, setSearchStatus] = useState('idle'); // idle | loading | ready | error
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const [showAll, setShowAll] = useState(false);
  const [retryTick, setRetryTick] = useState(0);
  const [announce, setAnnounce] = useState('');
  const [limitMessage, setLimitMessage] = useState('');
  const inputRef = useRef(null);
  const listRef = useRef(null);

  const listId = `${inputId}-listbox`;
  const hintId = `${inputId}-hint`;
  const errorId = `${inputId}-error`;
  const limitId = `${inputId}-limit`;

  useEffect(() => {
    const q = query.trim();
    if (!q) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setResults([]);
      setSearchStatus('idle');
      return undefined;
    }
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      setSearchStatus('loading');
      try {
        const data = await searchSkills(q, { signal: controller.signal });
        if (controller.signal.aborted) return;
        setResults(data.slice(0, 20));
        setSearchStatus('ready');
        setActive(0);
      } catch (err) {
        if (controller.signal.aborted || isCancelled(err)) return;
        setResults([]);
        setSearchStatus('error');
      }
    }, DEBOUNCE_MS);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query, retryTick]);

  const q = query.trim();
  const ql = q.toLowerCase();
  const added = new Set(value.map((s) => s.name.toLowerCase()));

  const options = results.map((s) => {
    const nameHit = s.name.toLowerCase().includes(ql);
    const alias = nameHit ? null : (s.aliases || []).find((a) => a.toLowerCase().includes(ql)) || null;
    return { type: 'skill', name: s.name, alias, added: added.has(s.name.toLowerCase()) };
  });
  const exact = results.some((s) => s.name.toLowerCase() === ql || (s.aliases || []).some((a) => a.toLowerCase() === ql));
  if (q && searchStatus !== 'loading' && !exact && !added.has(ql)) {
    options.push({ type: 'free', name: q, alias: null, added: false });
  }

  const activeIndex = Math.max(0, Math.min(active, options.length - 1));
  const listOpen = open && q.length > 0 && (options.length > 0 || searchStatus === 'loading');

  useEffect(() => {
    const list = listRef.current;
    if (!list || !listOpen) return;
    const el = list.querySelector(`[data-index="${activeIndex}"]`);
    if (!el) return;
    if (el.offsetTop < list.scrollTop) list.scrollTop = el.offsetTop;
    else if (el.offsetTop + el.offsetHeight > list.scrollTop + list.clientHeight) {
      list.scrollTop = el.offsetTop + el.offsetHeight - list.clientHeight;
    }
  }, [activeIndex, listOpen]);

  function pick(opt) {
    if (!opt) return;
    const nameLower = opt.name.trim().toLowerCase();
    if (opt.added || added.has(nameLower)) {
      setAnnounce(`${opt.name} is already added`);
      setQuery('');
      setOpen(false);
      return;
    }
    if (value.length >= CHIP_LIMIT) {
      setLimitMessage('You can add up to 30 skills. Remove one before adding more.');
      setAnnounce('Maximum of 30 skills reached. Remove one before adding more.');
      setQuery('');
      setOpen(false);
      return;
    }
    setLimitMessage('');
    onChange([...value, { name: opt.name, known: opt.type === 'skill' }]);
    setAnnounce(`${opt.name} added. ${value.length + 1} skills.`);
    setQuery('');
    setResults([]);
    setOpen(false);
    setActive(0);
  }

  function removeAt(index) {
    const removed = value[index];
    onChange(value.filter((_, i) => i !== index));
    setLimitMessage('');
    setAnnounce(`${removed.name} removed`);
    inputRef.current?.focus();
  }

  function onKeyDown(e) {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setOpen(true);
        setActive((a) => Math.min(a + 1, Math.max(options.length - 1, 0)));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setActive((a) => Math.max(a - 1, 0));
        break;
      case ',':
      case 'Enter':
        if (q) {
          e.preventDefault();
          if (added.has(ql)) {
            setAnnounce(`${q} is already added`);
            setQuery('');
            setOpen(false);
            return;
          }
          if (value.length >= CHIP_LIMIT) {
            setLimitMessage('You can add up to 30 skills. Remove one before adding more.');
            setAnnounce('Maximum of 30 skills reached. Remove one before adding more.');
            setQuery('');
            setOpen(false);
            return;
          }
          if (options.length) {
            pick(options[activeIndex]);
          } else {
            pick({ type: 'free', name: q });
          }
        }
        break;
      case 'Escape':
        if (q || open) {
          e.preventDefault();
          setQuery('');
          setResults([]);
          setOpen(false);
          setAnnounce('Search cleared');
        }
        break;
      case 'Backspace':
        if (!query && value.length) {
          e.preventDefault();
          removeAt(value.length - 1);
        }
        break;
      case 'Tab':
        setOpen(false);
        break;
      default:
        break;
    }
  }

  const visible = showAll || value.length <= CHIP_LIMIT ? value : value.slice(0, CHIP_LIMIT);

  return (
    <section className="min-w-0">
      <p className="sr-only" aria-live="polite">{announce}</p>

      <div className="mb-5 flex items-center gap-3">
        <StepNumber n="01" />
        <label htmlFor={inputId} className="flex-1 text-[14px] font-bold uppercase tracking-[1.5px] text-ink">
          Skills you already have
        </label>
        {value.length > 0 && (
          <span className="text-[13px] tabular-nums text-ink-3">
            {value.length} added{value.length >= CHIP_LIMIT ? ' (maximum)' : ''}
          </span>
        )}
      </div>

      <div className="relative">
        <Search size={18} strokeWidth={2} aria-hidden="true" className="pointer-events-none absolute left-4 top-[18px] text-ink-2" />
        <input
          ref={inputRef}
          id={inputId}
          type="text"
          role="combobox"
          autoComplete="off"
          autoCapitalize="off"
          spellCheck={false}
          aria-autocomplete="list"
          aria-expanded={listOpen}
          aria-controls={listId}
          aria-activedescendant={listOpen && options.length ? `${listId}-opt-${activeIndex}` : undefined}
          aria-describedby={[hintId, limitMessage ? limitId : null, searchStatus === 'error' ? errorId : null]
            .filter(Boolean)
            .join(' ')}
          placeholder="Search skills, like React or Python"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
            setActive(0);
          }}
          onFocus={() => setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 120)}
          onKeyDown={onKeyDown}
          className="min-h-[64px] w-full rounded-xl border border-line bg-surface py-3 pl-[50px] pr-4 text-[17px] font-medium text-ink transition-colors focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
        />

        {listOpen && (
          <ul
            ref={listRef}
            id={listId}
            role="listbox"
            aria-label="Matching skills"
            className="absolute inset-x-0 top-[calc(100%+8px)] z-30 max-h-[336px] overflow-auto rounded-xl border border-line bg-surface shadow-card"
          >
            {options.length === 0 && searchStatus === 'loading' && (
              <li role="presentation" className="px-4 py-3 text-sm text-ink-3">
                Searching…
              </li>
            )}
            {options.map((opt, i) => (
              <li
                key={`${opt.type}-${opt.name}`}
                id={`${listId}-opt-${i}`}
                data-index={i}
                role="option"
                aria-selected={i === activeIndex}
                aria-disabled={opt.added || undefined}
                onMouseDown={(e) => {
                  e.preventDefault();
                  pick(opt);
                }}
                onMouseEnter={() => setActive(i)}
                className={`flex min-h-[46px] cursor-pointer flex-wrap items-baseline justify-between gap-x-3 gap-y-0.5 border-b border-line px-4 py-3 last:border-b-0 ${
                  i === activeIndex ? 'bg-tint' : ''
                } ${opt.added ? 'text-ink-3' : 'text-ink'}`}
              >
                <span className={`min-w-0 [overflow-wrap:anywhere] ${opt.type === 'free' ? '' : 'font-semibold'}`}>
                  {opt.type === 'free' ? `Add “${opt.name}” as typed` : opt.name}
                </span>
                <span className="text-xs text-ink-3">
                  {opt.type === 'free' ? 'We may not recognise it' : opt.added ? 'Already added' : opt.alias ? `matches “${opt.alias}”` : ''}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {limitMessage && (
        <p id={limitId} role="alert" className="mt-2.5 text-sm font-semibold text-fit-ink">
          {limitMessage}
        </p>
      )}

      <p id={hintId} className="mb-5 mt-2.5 text-[13px] leading-normal text-ink-3">
        Aliases work, like “reactjs”, “k8s”, “sklearn”. ↑ ↓ to move, Enter to add, Esc to clear, Backspace removes the last skill.
      </p>

      {searchStatus === 'error' && (
        <p id={errorId} role="alert" className="-mt-2 mb-5 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-ink-2">
          <span>We couldn't load suggestions. You can still add “{q}” as typed.</span>
          <button
            type="button"
            onClick={() => setRetryTick((t) => t + 1)}
            className="min-h-11 font-semibold text-accent-ink underline underline-offset-[3px]"
          >
            Retry
          </button>
        </p>
      )}

      {value.length > 0 ? (
        <>
          <ul aria-label="Selected skills" className="flex flex-wrap gap-2">
            {visible.map((s, i) => (
              <Chip key={s.name} name={s.name} unrecognized={!s.known} onRemove={() => removeAt(i)} />
            ))}
          </ul>
          <div className="mt-2 flex flex-wrap gap-x-[18px]">
            {value.length > CHIP_LIMIT && (
              <button
                type="button"
                onClick={() => setShowAll((v) => !v)}
                className="min-h-11 text-sm font-semibold text-accent-ink underline underline-offset-[3px]"
              >
                {showAll ? 'Show fewer' : `Show all ${value.length}`}
              </button>
            )}
            {value.length >= 3 && (
              <button
                type="button"
                onClick={() => {
                  onChange([]);
                  setShowAll(false);
                  setAnnounce('All skills cleared');
                  inputRef.current?.focus();
                }}
                className="min-h-11 text-sm font-medium text-ink-3 hover:text-ink"
              >
                Clear all
              </button>
            )}
          </div>
        </>
      ) : (
        <p className="text-[15px] leading-normal text-ink-3">
          Your selected skills will appear here. Add at least 2. Languages, frameworks, tools and coursework like DBMS all count.
        </p>
      )}
    </section>
  );
}
