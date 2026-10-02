import { useState, useRef, useEffect } from 'react'
import { fetchSkills } from '../api/client'

// Fallback skills in case API is offline (so Sashang is never blocked)
const FALLBACK_SKILLS = [
  'Python', 'JavaScript', 'TypeScript', 'React', 'Node.js',
  'Docker', 'Kubernetes', 'AWS', 'SQL', 'PostgreSQL',
  'MongoDB', 'Git', 'FastAPI', 'Java', 'C++',
  'Go', 'GraphQL', 'CI/CD', 'Linux', 'Redis',
  'Django', 'Spring Boot', 'Terraform', 'Bash', 'HTML/CSS',
  'Tailwind CSS', 'Next.js', 'Apache Kafka', 'PyTorch', 'TensorFlow',
  'Pandas', 'NumPy', 'Scikit-learn', 'Express.js', 'Google Cloud (GCP)',
  'Microsoft Azure', 'Microservices', 'REST APIs', 'Elasticsearch', 'Jenkins'
]

export default function SkillInput({ selectedSkills, onAddSkill, onRemoveSkill, onApiStatusChange }) {
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [skillsList, setSkillsList] = useState(FALLBACK_SKILLS)
  const [isLoading, setIsLoading] = useState(false)
  const [isApiOffline, setIsApiOffline] = useState(false)
  const [isOpen, setIsOpen] = useState(false)
  const [highlightedIndex, setHighlightedIndex] = useState(-1)
  
  const containerRef = useRef(null)
  const inputRef = useRef(null)

  // 1. Debounce the search input by 200ms
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query)
    }, 200)

    return () => clearTimeout(timer)
  }, [query])

  // 2. Fetch skills from API (/skills?q=...) whenever debouncedQuery changes
  useEffect(() => {
    let isCancelled = false

    async function loadSkills() {
      setIsLoading(true)
      try {
        const data = await fetchSkills(debouncedQuery)
        if (isCancelled) return

        // Support both: [{ skill_id, name, aliases }] and string[]
        const normalized = Array.isArray(data)
          ? data.map(item => (typeof item === 'string' ? item : item.name || item.skill_id))
          : FALLBACK_SKILLS

        setSkillsList(normalized)
        setIsApiOffline(false)
        if (onApiStatusChange) onApiStatusChange(true)
      } catch {
        if (isCancelled) return
        // API offline or error -> gracefully fallback to local skills
        setIsApiOffline(true)
        if (onApiStatusChange) onApiStatusChange(false)
        const filtered = FALLBACK_SKILLS.filter(s =>
          s.toLowerCase().includes(debouncedQuery.trim().toLowerCase())
        )
        setSkillsList(filtered)
      } finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadSkills()

    return () => {
      isCancelled = true
    }
  }, [debouncedQuery, onApiStatusChange])

  // Filter out already selected skills
  const availableSkills = skillsList.filter(
    skill => !selectedSkills.includes(skill)
  )

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false)
        setHighlightedIndex(-1)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSelect = (skill) => {
    onAddSkill(skill)
    setQuery('')
    setIsOpen(false)
    setHighlightedIndex(-1)
    inputRef.current?.focus()
  }

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      if (!isOpen) {
        setIsOpen(true)
      } else {
        setHighlightedIndex(prev =>
          prev < availableSkills.length - 1 ? prev + 1 : 0
        )
      }
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setHighlightedIndex(prev =>
        prev > 0 ? prev - 1 : availableSkills.length - 1
      )
    } else if (e.key === 'Enter') {
      e.preventDefault()
      if (isOpen && highlightedIndex >= 0 && highlightedIndex < availableSkills.length) {
        handleSelect(availableSkills[highlightedIndex])
      } else if (availableSkills.length > 0 && query.trim() !== '') {
        handleSelect(availableSkills[0])
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false)
      setHighlightedIndex(-1)
    }
  }

  return (
    <div className="w-full space-y-3" ref={containerRef}>
      <div className="flex items-center justify-between">
        <label className="block text-sm font-semibold tracking-wide text-slate-300">
          Your Skills <span className="text-emerald-400">*</span>
          <span className="ml-2 text-xs font-normal text-slate-500">
            (select at least 2)
          </span>
        </label>

        {/* Live / Offline badge */}
        <div className="flex items-center gap-1.5 text-[11px]">
          {isApiOffline ? (
            <span className="text-amber-400/90 flex items-center gap-1 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
              Local Fallback (API Offline)
            </span>
          ) : (
            <span className="text-emerald-400 flex items-center gap-1 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              API Live (/skills?q=)
            </span>
          )}
        </div>
      </div>

      {/* Selected Chips */}
      {selectedSkills.length > 0 && (
        <div className="flex flex-wrap gap-2 p-2.5 bg-slate-950/60 rounded-xl border border-slate-800/80 min-h-12 items-center">
          {selectedSkills.map(skill => (
            <span
              key={skill}
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs sm:text-sm font-medium bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 transition-all hover:bg-emerald-500/25"
            >
              <span>{skill}</span>
              <button
                type="button"
                onClick={() => onRemoveSkill(skill)}
                className="hover:text-red-400 hover:bg-red-500/20 rounded p-0.5 transition-colors focus:outline-none focus:ring-1 focus:ring-red-400"
                aria-label={`Remove ${skill}`}
              >
                <svg className="w-3.5 h-3.5" viewBox="0 0 14 14" fill="none">
                  <path
                    d="M3.5 3.5L10.5 10.5M10.5 3.5L3.5 10.5"
                    stroke="currentColor"
                    strokeWidth="1.75"
                    strokeLinecap="round"
                  />
                </svg>
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Autocomplete Input with 200ms Debounce Indicator */}
      <div className="relative">
        <div className="relative">
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value)
              setIsOpen(true)
            }}
            onFocus={() => setIsOpen(true)}
            onKeyDown={handleKeyDown}
            placeholder={
              selectedSkills.length === 0
                ? "Search skills (e.g. Python, Docker, React)..."
                : "Add another skill..."
            }
            className="w-full px-4 py-3 pl-10 pr-20 rounded-xl bg-slate-900 border border-slate-800 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-emerald-500/60 focus:ring-2 focus:ring-emerald-500/20 transition-all shadow-inner"
          />
          
          {/* Left search icon */}
          <div className="absolute left-3.5 top-3.5 text-slate-500 pointer-events-none">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>

          {/* Right status: Loading spinner or Clear button */}
          <div className="absolute right-3.5 top-3 flex items-center gap-2">
            {isLoading && (
              <svg className="animate-spin h-4 w-4 text-emerald-400" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
              </svg>
            )}
            {query && (
              <button
                type="button"
                onClick={() => {
                  setQuery('')
                  setIsOpen(false)
                }}
                className="text-slate-400 hover:text-slate-200 text-xs px-1.5 py-0.5 rounded bg-slate-800"
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Dropdown Options */}
        {isOpen && (
          <div className="absolute z-20 left-0 right-0 mt-2 max-h-60 overflow-y-auto rounded-xl bg-slate-900/95 backdrop-blur-md border border-slate-700/80 shadow-2xl divide-y divide-slate-800/50">
            {availableSkills.length > 0 ? (
              availableSkills.map((skill, index) => (
                <button
                  key={skill}
                  type="button"
                  onClick={() => handleSelect(skill)}
                  onMouseEnter={() => setHighlightedIndex(index)}
                  className={`w-full text-left px-4 py-2.5 text-sm transition-colors flex items-center justify-between ${
                    index === highlightedIndex
                      ? 'bg-emerald-500/20 text-emerald-200'
                      : 'text-slate-300 hover:bg-slate-800/60'
                  }`}
                >
                  <span className="font-medium">{skill}</span>
                  <span className="text-xs text-slate-500">+ Add</span>
                </button>
              ))
            ) : (
              <div className="px-4 py-3 text-xs text-slate-500 text-center">
                {isLoading
                  ? 'Searching skills...'
                  : query.trim() === ''
                  ? 'All available skills are already selected'
                  : `No skills matching "${query}"`}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
