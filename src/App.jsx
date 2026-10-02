import { useState, useEffect } from 'react'
import SkillInput from './components/SkillInput'
import RoleSelect from './components/RoleSelect'
import MatchPanel from './components/MatchPanel'
import ReadinessPanel from './components/ReadinessPanel'
import GapPanel from './components/GapPanel'
import { checkApiHealth, fetchMatch, API_BASE_URL } from './api/client'

// Fallback fixture generator to ensure Sashang is NEVER blocked
function generateFallbackMatches(skills, desiredRole) {
  const roleWeights = [
    { role: 'DevOps Engineer', keywords: ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux', 'Terraform', 'Jenkins', 'Bash'] },
    { role: 'Frontend Developer', keywords: ['JavaScript', 'TypeScript', 'React', 'HTML/CSS', 'Tailwind CSS', 'Next.js', 'Vite'] },
    { role: 'Backend Developer', keywords: ['Python', 'Node.js', 'FastAPI', 'Java', 'SQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Django', 'Express.js', 'Go'] },
    { role: 'Full Stack Engineer', keywords: ['React', 'JavaScript', 'Node.js', 'SQL', 'MongoDB', 'TypeScript', 'REST APIs', 'Express.js'] },
    { role: 'Data Engineer', keywords: ['Python', 'SQL', 'PostgreSQL', 'Apache Kafka', 'Pandas', 'NumPy', 'AWS', 'Redis'] },
    { role: 'Machine Learning Engineer', keywords: ['Python', 'PyTorch', 'TensorFlow', 'Pandas', 'NumPy', 'Scikit-learn', 'SQL'] },
    { role: 'Cloud Architect', keywords: ['AWS', 'Google Cloud (GCP)', 'Microsoft Azure', 'Terraform', 'Kubernetes', 'Docker', 'Microservices'] }
  ]

  // Calculate score based on keyword intersection
  const scoredRoles = roleWeights.map(item => {
    let matchCount = 0
    skills.forEach(s => {
      if (item.keywords.some(k => k.toLowerCase() === s.toLowerCase())) {
        matchCount += 1
      }
    })
    // Boost desired role slightly if selected
    if (desiredRole && item.role.toLowerCase() === desiredRole.toLowerCase()) {
      matchCount += 0.5
    }
    const rawProb = Math.min(0.92, Math.max(0.35, (matchCount / Math.max(skills.length, 3)) * 0.8 + 0.35))
    return {
      role: item.role,
      probability: Math.round(rawProb * 100) / 100
    }
  })

  // Sort by probability descending
  scoredRoles.sort((a, b) => b.probability - a.probability)

  // Ensure desiredRole is included in top 3 if it has reasonable score
  const top3 = scoredRoles.slice(0, 3)
  const desiredInTop3 = top3.some(r => r.role.toLowerCase() === desiredRole.toLowerCase())
  if (!desiredInTop3 && desiredRole) {
    const desiredMatch = scoredRoles.find(r => r.role.toLowerCase() === desiredRole.toLowerCase())
    if (desiredMatch) {
      top3[2] = desiredMatch
    }
  }

  // Check for unrecognized skills (if any skill is outside standard list)
  const knownTokens = roleWeights.flatMap(r => r.keywords.map(k => k.toLowerCase()))
  const unrecognized = skills.filter(s => !knownTokens.includes(s.toLowerCase()) && !['c++', 'rest apis', 'elasticsearch', 'spring boot'].includes(s.toLowerCase()))

  return {
    matches: top3,
    unrecognized
  }
}

function App() {
  const [selectedSkills, setSelectedSkills] = useState([])
  const [desiredRole, setDesiredRole] = useState('')
  const [viewMode, setViewMode] = useState('input') // 'input' | 'result'
  const [matchData, setMatchData] = useState({ matches: [], unrecognized: [] })
  const [isLoadingMatch, setIsLoadingMatch] = useState(false)
  const [apiStatus, setApiStatus] = useState('checking') // 'online' | 'offline'

  // Probe API health on mount
  useEffect(() => {
    let isCancelled = false

    async function probeApi() {
      try {
        await checkApiHealth()
        if (!isCancelled) setApiStatus('online')
      } catch {
        if (!isCancelled) setApiStatus('offline')
      }
    }

    probeApi()
    const interval = setInterval(probeApi, 15000)

    return () => {
      isCancelled = true
      clearInterval(interval)
    }
  }, [])

  const handleAddSkill = (skill) => {
    if (!selectedSkills.includes(skill)) {
      setSelectedSkills(prev => [...prev, skill])
    }
  }

  const handleRemoveSkill = (skillToRemove) => {
    setSelectedSkills(prev => prev.filter(skill => skill !== skillToRemove))
  }

  // Validation: at least 2 skills and a chosen role
  const hasEnoughSkills = selectedSkills.length >= 2
  const hasSelectedRole = desiredRole.trim() !== ''
  const isFormValid = hasEnoughSkills && hasSelectedRole

  const getDisabledReason = () => {
    if (!hasEnoughSkills && !hasSelectedRole) {
      return 'Select at least 2 skills and choose a target role'
    }
    if (!hasEnoughSkills) {
      return `Add at least ${2 - selectedSkills.length} more skill${2 - selectedSkills.length > 1 ? 's' : ''}`
    }
    if (!hasSelectedRole) {
      return 'Please choose a target role'
    }
    return ''
  }

  // Submit and transition to Result State (Day 4)
  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!isFormValid) return

    setIsLoadingMatch(true)
    setViewMode('result')

    const payload = {
      skills: selectedSkills,
      desired_role: desiredRole
    }
    console.log('Analyzing job fit with payload:', payload)

    try {
      // 1. Call POST /match on API
      const res = await fetchMatch(selectedSkills)
      if (res && res.matches) {
        setMatchData({
          matches: res.matches,
          unrecognized: res.unrecognized || []
        })
      } else {
        // Fallback if API returned empty/unexpected structure
        setMatchData(generateFallbackMatches(selectedSkills, desiredRole))
      }
    } catch (err) {
      // 2. Local realistic fixture fallback so Sashang is NEVER blocked
      console.warn('API /match unavailable, using realistic local fixtures:', err.message)
      setMatchData(generateFallbackMatches(selectedSkills, desiredRole))
    } finally {
      setIsLoadingMatch(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-slate-100 flex flex-col justify-between p-4 sm:p-6 lg:p-8">
      {/* Top Header */}
      <header className="max-w-3xl mx-auto w-full text-center pt-4 sm:pt-6 pb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-4">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          Day 4 · Result Layout & MatchPanel
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-emerald-400 via-teal-200 to-cyan-400 bg-clip-text text-transparent">
          SkillGraph
        </h1>
        <p className="mt-2 text-slate-400 text-sm sm:text-base font-normal max-w-lg mx-auto">
          India Job Market Mining Engine · Discover role fit, readiness & high-impact skill gaps
        </p>
      </header>

      {/* Main Content Area */}
      <main className="max-w-2xl mx-auto w-full space-y-6">
        {/* API Status Notice */}
        {apiStatus === 'offline' && (
          <div className="flex items-start gap-3 p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200 text-xs">
            <svg className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <div className="font-semibold text-amber-300">Fixture API Unreachable ({API_BASE_URL})</div>
              <p className="text-amber-400/80 mt-0.5">
                Archit's local server isn't running yet. Running in unblocked fixture fallback mode with real market heuristics.
              </p>
            </div>
          </div>
        )}

        {/* -------------------- STATE 1: INPUT STATE -------------------- */}
        {viewMode === 'input' && (
          <form
            onSubmit={handleSubmit}
            className="bg-slate-900/70 border border-slate-800 backdrop-blur-xl rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6"
          >
            {/* Skill Selector Component */}
            <SkillInput
              selectedSkills={selectedSkills}
              onAddSkill={handleAddSkill}
              onRemoveSkill={handleRemoveSkill}
              onApiStatusChange={(isOnline) => setApiStatus(isOnline ? 'online' : 'offline')}
            />

            {/* Role Dropdown Component */}
            <RoleSelect
              desiredRole={desiredRole}
              onChangeRole={setDesiredRole}
            />

            {/* Submit Button Section */}
            <div className="pt-2">
              <div className="group relative">
                <button
                  type="submit"
                  disabled={!isFormValid}
                  title={!isFormValid ? getDisabledReason() : 'Submit for role fit analysis'}
                  className={`w-full py-3.5 px-6 rounded-xl font-semibold text-sm transition-all duration-200 flex items-center justify-center gap-2 shadow-lg ${
                    isFormValid
                      ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 hover:from-emerald-400 hover:to-teal-400 active:scale-[0.99] cursor-pointer shadow-emerald-950/40'
                      : 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700/50'
                  }`}
                >
                  <span>Analyze Job Market Fit</span>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </button>

                {!isFormValid && (
                  <div className="hidden group-hover:block absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1.5 bg-slate-800 border border-slate-700 text-xs text-amber-300 rounded-lg shadow-xl whitespace-nowrap z-30">
                    {getDisabledReason()}
                  </div>
                )}
              </div>

              <div className="mt-2 text-center text-xs">
                {!isFormValid ? (
                  <span className="text-amber-400/90 font-medium">
                    {getDisabledReason()}
                  </span>
                ) : (
                  <span className="text-emerald-400 font-medium">
                    Ready to analyze! Click to view 3-panel market report.
                  </span>
                )}
              </div>
            </div>
          </form>
        )}

        {/* -------------------- STATE 2: RESULT STATE (Day 4) -------------------- */}
        {viewMode === 'result' && (
          <div className="space-y-6">
            {/* Top Navigation & Profile Summary */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/60 border border-slate-800/90">
              <button
                type="button"
                onClick={() => setViewMode('input')}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold text-slate-300 bg-slate-800/80 hover:bg-slate-700 hover:text-white border border-slate-700/80 transition-all cursor-pointer w-fit"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                ← Back to Edit Skills
              </button>

              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="text-slate-400">Target Role:</span>
                <span className="px-2.5 py-1 rounded-lg bg-emerald-500/15 text-emerald-300 font-semibold border border-emerald-500/30">
                  {desiredRole}
                </span>
                <span className="text-slate-500">·</span>
                <span className="text-slate-400">{selectedSkills.length} Skills Submitted</span>
              </div>
            </div>

            {/* THREE STACKED CARDS (Ordered per Notion spec) */}
            <div className="space-y-6">
              {/* Card 1: Readiness Panel (Day 5 target) */}
              <ReadinessPanel
                desiredRole={desiredRole}
                selectedSkills={selectedSkills}
              />

              {/* Card 2: What to Learn Next (Day 6 target) */}
              <GapPanel
                desiredRole={desiredRole}
              />

              {/* Card 3: Roles That Actually Fit You (Day 4 Core Build) */}
              <MatchPanel
                matches={matchData.matches}
                unrecognized={matchData.unrecognized}
                desiredRole={desiredRole}
                isLoading={isLoadingMatch}
              />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="text-center text-xs text-slate-600 py-6">
        SkillGraph Sprint · Frontend Module
      </footer>
    </div>
  )
}

export default App