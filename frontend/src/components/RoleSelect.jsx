import { useState, useEffect } from 'react'
import { fetchRoles } from '../api/client'

const FALLBACK_ROLES = [
  'Data Engineer',
  'Frontend Developer',
  'Backend Developer',
  'Full Stack Engineer',
  'DevOps Engineer',
  'Machine Learning Engineer',
  'Cloud Architect',
  'Security Engineer'
]

export default function RoleSelect({ desiredRole, onChangeRole }) {
  const [roles, setRoles] = useState(FALLBACK_ROLES)
  const [isLoading, setIsLoading] = useState(false)
  const [isOffline, setIsOffline] = useState(false)

  useEffect(() => {
    let isCancelled = false

    async function loadRoles() {
      setIsLoading(true)
      try {
        const data = await fetchRoles()
        if (isCancelled) return

        // Support [{ role_family, ... }] or string[]
        const normalized = Array.isArray(data)
          ? data.map(item => (typeof item === 'string' ? item : item.role_family || item.name))
          : FALLBACK_ROLES

        setRoles(normalized)
        setIsOffline(false)
      } catch {
        if (isCancelled) return
        setIsOffline(true)
        setRoles(FALLBACK_ROLES)
      } finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadRoles()

    return () => {
      isCancelled = true
    }
  }, [])

  return (
    <div className="w-full space-y-2">
      <div className="flex items-center justify-between">
        <label htmlFor="role-select" className="block text-sm font-semibold tracking-wide text-slate-300">
          Desired Role <span className="text-emerald-400">*</span>
        </label>
        {isOffline && (
          <span className="text-[11px] text-amber-400/80">
            (fallback roles)
          </span>
        )}
      </div>

      <div className="relative">
        <select
          id="role-select"
          value={desiredRole}
          onChange={(e) => onChangeRole(e.target.value)}
          disabled={isLoading}
          className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-100 text-sm focus:outline-none focus:border-emerald-500/60 focus:ring-2 focus:ring-emerald-500/20 transition-all appearance-none cursor-pointer shadow-inner pr-10 disabled:opacity-50"
        >
          <option value="" disabled className="text-slate-500">
            {isLoading ? 'Loading roles from API...' : 'Choose a target role...'}
          </option>
          {roles.map((role) => (
            <option key={role} value={role} className="bg-slate-900 text-slate-100 py-1">
              {role}
            </option>
          ))}
        </select>

        <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500">
          {isLoading ? (
            <svg className="animate-spin h-4 w-4 text-emerald-400" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
            </svg>
          )}
        </div>
      </div>
    </div>
  )
}
