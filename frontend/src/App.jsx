import { useEffect, useRef, useState } from 'react';
import { ArrowLeft, ArrowRight, CircleAlert, CloudOff, Info, RefreshCw, RotateCcw, Server } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Lenis from 'lenis';
import { analyze, getRoles, getHealth, isCancelled, toFriendlyError } from './api/client';
import SkillInput from './components/SkillInput';
import RoleSelect from './components/RoleSelect';
import ReadinessPanel from './components/ReadinessPanel';
import GapPanel from './components/GapPanel';
import MatchPanel from './components/MatchPanel';
import RoleSkillMix from './components/ui/RoleSkillMix';
import Card from './components/ui/Card';
import { SkeletonBarRow } from './components/ui/Skeleton';
import Skeleton from './components/ui/Skeleton';
import { fadeUp, staggerContainer, maskReveal, viewTransition } from './animations';

const MIN_SKILLS = 2;
const AUTO_RETRY_SECONDS = 15;
const WAKING_AFTER_SECONDS = 4;
const SKILL_INPUT_ID = 'skill-search';

const container = 'mx-auto max-w-[1100px] px-5 sm:px-6';
const eyebrow = 'mb-8 inline-flex items-center gap-2.5 rounded-full border border-accent-line/40 bg-accent-tint/50 px-3.5 py-1.5 text-[12.5px] font-bold uppercase tracking-[1.5px] text-accent-ink shadow-sm backdrop-blur-sm';
const primaryBtn =
  'group inline-flex min-h-[56px] items-center gap-2 rounded-xl btn-gradient px-6 text-[16px] font-bold text-white transition-all duration-300 hover:-translate-y-0.5 hover:shadow-[0_8px_20px_-4px_rgba(28,167,236,0.4)] disabled:opacity-50 disabled:hover:shadow-none disabled:hover:translate-y-0';
const secondaryBtn =
  'group inline-flex min-h-[56px] flex-none items-center gap-2.5 whitespace-nowrap rounded-xl border border-line-2 bg-surface px-6 text-[16px] font-bold text-ink transition-all duration-200 hover:border-ink-3 hover:bg-tint hover:shadow-sm';

function disabledReason(count, role) {
  const need = Math.max(0, MIN_SKILLS - count);
  if (need && !role) {
    return count === 0 ? 'Add at least 2 skills and choose a target role to continue.' : 'Add 1 more skill and choose a target role to continue.';
  }
  if (need) return count === 0 ? 'Add at least 2 skills to continue.' : 'Add 1 more skill to continue, one skill isn’t enough to compare against postings.';
  if (!role) return 'Choose the role you’re aiming for to continue.';
  return null;
}

function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-line" style={{ backgroundColor: 'rgba(255,255,255,0.78)', backdropFilter: 'blur(16px)' }}>
      <div className={`${container} flex items-center gap-4 py-3`}>
        <motion.div 
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex flex-none items-center gap-3 cursor-pointer"
        >
          <span aria-hidden="true" className="grid size-10 place-items-center rounded-xl btn-gradient text-[18px] font-bold text-white shadow-logo">
            S
          </span>
          <span className="text-[20px] font-bold tracking-tight text-ink">SkillGraph</span>
        </motion.div>
        <span className="ml-auto hidden items-center gap-2 rounded-full border border-line-2 bg-surface px-3 py-1 text-[13px] font-medium text-ink-2 shadow-sm sm:inline-flex">
          <span className="relative flex size-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-75"></span>
            <span className="relative inline-flex size-2 rounded-full bg-accent"></span>
          </span>
          12,872 Indian tech jobs analyzed
        </span>
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer className="flex flex-col sm:flex-row justify-between gap-x-4 gap-y-3 border-t border-line pb-12 pt-8 text-[13px] leading-normal text-ink-3">
      <span>Estimates from posting data, not hiring guarantees.</span>
      <span>12,872 labelled Indian tech job postings · 10 role families · India</span>
    </footer>
  );
}

export default function App() {
  const [selectedSkills, setSelectedSkills] = useState([]); // [{ name, known }]
  const [desiredRole, setDesiredRole] = useState('');
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState('idle'); // idle | loading | success | error
  const [error, setError] = useState(null);
  const [view, setView] = useState('input'); // input | results
  const [lastPayload, setLastPayload] = useState(null);
  const [elapsed, setElapsed] = useState(0);

  const [roles, setRoles] = useState([]);
  const [rolesStatus, setRolesStatus] = useState('loading'); // loading | ready | error
  const [retryIn, setRetryIn] = useState(0);
  const [healthFailed, setHealthFailed] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);

  const abortRef = useRef(null);
  const resultsHeadingRef = useRef(null);
  const isSubmittingRef = useRef(false);

  function loadRoles() {
    setRolesStatus('loading');
    setRetryIn(0);
    getRoles()
      .then((data) => {
        setRoles(data);
        setRolesStatus('ready');
      })
      .catch(() => {
        setRolesStatus('error');
        setRetryIn(AUTO_RETRY_SECONDS);
      });
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadRoles();
    getHealth().catch(() => setHealthFailed(true));

    const lenis = new Lenis({ lerp: 0.05, wheelMultiplier: 0.8, smoothWheel: true });
    function raf(time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    const handleScroll = () => {
      const h = document.documentElement;
      const progress = h.scrollTop / (h.scrollHeight - h.clientHeight) || 0;
      setScrollProgress(progress);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      abortRef.current?.abort();
      window.removeEventListener('scroll', handleScroll);
      lenis.destroy();
    };
  }, []);

  // Auto-retry /roles with a visible countdown.
  useEffect(() => {
    if (rolesStatus !== 'error' || retryIn <= 0) return undefined;
    const t = setTimeout(() => {
      if (retryIn <= 1) loadRoles();
      else setRetryIn(retryIn - 1);
    }, 1000);
    return () => clearTimeout(t);
  }, [rolesStatus, retryIn]);

  // Elapsed seconds while /analyze is in flight.
  useEffect(() => {
    if (status !== 'loading') return undefined;
    const started = Date.now();
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setElapsed(0);
    const id = setInterval(() => setElapsed((Date.now() - started) / 1000), 250);
    return () => clearInterval(id);
  }, [status, lastPayload]);

  // Move focus to the results heading after submit and when results or error change.
  useEffect(() => {
    if (view === 'results') {
      // Focus handled via AnimatePresence onExitComplete below
    }
  }, [view, status]);

  async function runAnalyze(payload) {
    if (isSubmittingRef.current) return;
    isSubmittingRef.current = true;
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setLastPayload(payload);
    setResult(null);
    setError(null);
    setStatus('loading');
    setView('results');
    try {
      const data = await analyze(payload, { signal: controller.signal });
      if (controller.signal.aborted) return;
      setResult(data);
      setStatus('success');
    } catch (err) {
      if (controller.signal.aborted || isCancelled(err)) return;
      setError(toFriendlyError(err));
      setStatus('error');
    } finally {
      isSubmittingRef.current = false;
    }
  }

  const skillNames = selectedSkills.map((s) => s.name);
  const reason = disabledReason(selectedSkills.length, desiredRole);
  const canSubmit = !reason && rolesStatus === 'ready';

  function handleSubmit(e) {
    e.preventDefault();
    if (!canSubmit || isSubmittingRef.current || status === 'loading') return;
    runAnalyze({ skills: skillNames, desired_role: desiredRole });
  }

  function handleEdit() {
    abortRef.current?.abort();
    setStatus('idle');
    setView('input');
  }

  function handleRetry() {
    if (lastPayload) runAnalyze(lastPayload);
  }

  function handleSwitchRole(role) {
    if (!role || !lastPayload) return;
    setDesiredRole(role);
    runAnalyze({ skills: lastPayload.skills, desired_role: role });
  }

  const shownRole = lastPayload?.desired_role || desiredRole;
  const shownSkills = lastPayload?.skills || skillNames;
  const skillSummary = shownSkills.length > 6 ? `${shownSkills.slice(0, 6).join(', ')} + ${shownSkills.length - 6} more` : shownSkills.join(', ');
  const roleInfo = roles.find((r) => r.role_family === shownRole);

  let liveMessage = '';
  if (view === 'results' && status === 'loading') liveMessage = elapsed >= WAKING_AFTER_SECONDS ? 'Waking the server up, the first request takes a few seconds.' : 'Checking your skills.';
  if (status === 'success' && result) {
    liveMessage = `Readiness for ${shownRole}: ${Math.round(result.readiness.probability * 100)} percent, ${result.readiness.band}.`;
  }

  const waking = elapsed >= WAKING_AFTER_SECONDS;
  const unrecognized = result?.match?.unrecognized || [];

  return (
    <div className="min-h-screen bg-bg text-ink">
      <div 
        className="fixed top-0 left-0 h-[2px] bg-accent z-50 transition-[width] duration-75 ease-out" 
        style={{ width: `${scrollProgress * 100}%` }} 
      />
      <p className="sr-only" aria-live="polite" aria-atomic="true">
        {liveMessage}
      </p>
      <Header />
      {healthFailed && (
        <div className="bg-surface border-b border-line px-5 py-2 text-center text-sm text-ink-2">
          <CircleAlert size={16} strokeWidth={2} className="inline-block mr-1.5 -mt-0.5" aria-hidden="true" />
          The server is offline or waking up. Your first request might take a few extra seconds.
        </div>
      )}

      <main className={container}>
        <AnimatePresence 
          mode="wait" 
          onExitComplete={() => {
            window.scrollTo({ top: 0, behavior: 'instant' });
            if (view === 'results') {
              setTimeout(() => resultsHeadingRef.current?.focus({ preventScroll: true }), 50);
            } else {
              setTimeout(() => document.getElementById(SKILL_INPUT_ID)?.focus({ preventScroll: true }), 50);
            }
          }}
        >
        {view === 'input' && (
          <motion.div key="input" variants={viewTransition} initial="hidden" animate="visible" exit="exit" className="relative">
            <div className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-[600px] w-full overflow-hidden [mask-image:linear-gradient(to_bottom,black_40%,transparent_100%)]">
              <div className="hero-orb w-[500px] h-[500px] top-[-100px] left-[-100px] bg-[radial-gradient(circle,rgba(123,213,245,0.25)_0%,transparent_70%)]" style={{ animationDuration: '25s' }} />
              <div className="hero-orb w-[600px] h-[600px] top-[-50px] right-[-150px] bg-[radial-gradient(circle,rgba(120,127,246,0.18)_0%,transparent_70%)]" style={{ animationDuration: '22s', animationDelay: '-5s' }} />
              <div className="hero-orb w-[400px] h-[400px] top-[20%] left-[30%] bg-[radial-gradient(circle,rgba(74,222,222,0.15)_0%,transparent_70%)]" style={{ animationDuration: '28s', animationDelay: '-10s' }} />
            </div>
            <motion.section 
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-80px" }}
              className="pb-[clamp(28px,5vw,44px)] pt-[clamp(36px,8vw,72px)]"
            >
              <motion.div variants={fadeUp}>
                <span className={eyebrow}>
                  <span className="size-1.5 rounded-full bg-accent inline-block animate-pulse" />
                  Placement prep, made honest
                </span>
              </motion.div>
              <h1 className="text-[clamp(44px,7vw,80px)] font-extrabold leading-[1] tracking-tight md:tracking-tighter">
                <span className="block overflow-hidden"><motion.span variants={maskReveal} className="block">Know what to learn</motion.span></span>
                <span className="block overflow-hidden pb-[0.06em]">
                  <motion.span 
                    variants={maskReveal} 
                    className="text-gradient block bg-[length:200%_auto] animate-[bg-pan_8s_linear_infinite]"
                  >
                    before you apply.
                  </motion.span>
                </span>
              </h1>
              <motion.p variants={fadeUp} className="mt-6 max-w-[640px] text-[18px] md:text-[19px] font-medium leading-[1.55] text-ink-2 text-pretty">
                See how your current skills line up with the roles Indian tech companies are hiring for, based on 12,872 labelled Indian tech job postings.
              </motion.p>
            </motion.section>

            {rolesStatus === 'error' && (
              <Card as="section" tone="notice" shadow={false} role="alert" className="mb-9 grid grid-cols-[auto_minmax(0,1fr)] gap-3.5">
                <CloudOff size={22} strokeWidth={2} className="mt-0.5 text-ink-2" aria-hidden="true" />
                <div>
                  <h2 className="mb-1.5 text-[19px] font-bold tracking-[-0.02em]">We can't reach SkillGraph right now</h2>
                  <p className="mb-1.5 max-w-[58ch] text-[15px] leading-[1.55] text-ink-2 text-pretty">
                    The roles load from our server, which is either waking up or briefly offline. Nothing you did caused this. Your skills are kept.
                  </p>
                  <p className="mb-4 text-sm text-ink-3">
                    {retryIn > 0
                      ? `We'll try again automatically in ${retryIn} s. Free servers can take up to 25 seconds to wake up.`
                      : 'Trying again…'}
                  </p>
                  <button type="button" onClick={loadRoles} className={primaryBtn.replace('min-h-[46px]', 'min-h-11')}>
                    <RefreshCw size={16} strokeWidth={2} aria-hidden="true" />
                    Try again now
                  </button>
                </div>
              </Card>
            )}

            <motion.form 
              onSubmit={handleSubmit} 
              noValidate
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-80px" }}
              variants={staggerContainer}
            >
              <div className="grid grid-cols-1 items-start gap-11 md:grid-cols-2 md:gap-x-[72px]">
                <SkillInput value={selectedSkills} onChange={setSelectedSkills} inputId={SKILL_INPUT_ID} />
                <RoleSelect roles={roles} status={rolesStatus} value={desiredRole} onChange={setDesiredRole} selectedNames={skillNames} />
              </div>

              <div className="mt-10 flex flex-wrap items-center gap-x-8 gap-y-5 border-t border-line pb-8 pt-6">
                <p id="submit-reason" aria-live="polite" className="flex flex-[1_1_260px] items-start gap-2 text-[15px] font-medium leading-[1.45] text-ink-2 text-pretty">
                  {reason && <Info size={18} strokeWidth={2} className="mt-[3px] flex-none" aria-hidden="true" />}
                  <span>
                    {reason ||
                      (rolesStatus === 'ready'
                        ? `Ready to check ${selectedSkills.length} skills against ${desiredRole}.`
                        : 'Waiting for the role list to load.')}
                  </span>
                </p>
                <motion.button
                  whileTap={{ scale: 0.97 }}
                  type="submit"
                  disabled={!canSubmit || status === 'loading'}
                  aria-describedby="submit-reason"
                  className={`${primaryBtn} max-w-[360px] flex-[1_1_260px] justify-between`}
                >
                  Show my skill map
                  <ArrowRight size={20} strokeWidth={2.5} aria-hidden="true" className="transition-transform duration-300 group-hover:translate-x-1" />
                </motion.button>
              </div>
            </motion.form>
          </motion.div>
        )}

        {view === 'results' && (
          <motion.div id="results-region" key="results" aria-live="polite" variants={viewTransition} initial="hidden" animate="visible" exit="exit">
            <motion.section 
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-80px" }}
              className="flex flex-wrap items-end justify-between gap-x-6 gap-y-5 pb-7 pt-[clamp(40px,9vw,88px)]"
            >
              <div className="min-w-0 flex-[1_1_420px]">
                <motion.p variants={fadeUp} className={eyebrow}>{status === 'loading' ? 'Building your skill map' : 'Your skill map'}</motion.p>
                <h1
                  ref={resultsHeadingRef}
                  tabIndex={-1}
                  className="text-[clamp(40px,9vw,64px)] font-semibold leading-[1.03] tracking-[-0.05em] outline-none"
                >
                  <span className="block overflow-hidden">
                    <motion.span variants={maskReveal} className="block">
                      {status === 'loading' ? 'Reading the postings' : status === 'error' ? 'Almost there,' : 'Here’s your honest'}
                    </motion.span>
                  </span>
                  <span className="block overflow-hidden">
                    <motion.span variants={maskReveal} className="text-gradient block pb-[0.15em]">
                      {status === 'loading' ? 'for you.' : status === 'error' ? 'one more try.' : 'starting point.'}
                    </motion.span>
                  </span>
                </h1>
                <motion.p variants={fadeUp} className="mt-4 text-sm leading-normal text-ink-3 [overflow-wrap:anywhere]">
                  <strong className="font-semibold text-ink-2">{shownRole}</strong> · {shownSkills.length} skill{shownSkills.length === 1 ? '' : 's'}: {skillSummary}
                </motion.p>
              </div>
              <motion.div variants={fadeUp}>
                <motion.button whileTap={{ scale: 0.97 }} type="button" onClick={handleEdit} className={secondaryBtn}>
                  <ArrowLeft size={16} strokeWidth={2} aria-hidden="true" className="transition-transform duration-300 group-hover:-translate-x-1" />
                  {status === 'loading' ? 'Cancel and edit' : 'Edit my answers'}
                </motion.button>
              </motion.div>
            </motion.section>

            {status === 'loading' && (
              <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
                <Card tone="status" shadow={false} role="status" className="grid grid-cols-[auto_minmax(0,1fr)] gap-4">
                  <Server size={24} strokeWidth={2} className="mt-0.5 text-accent-ink" aria-hidden="true" />
                  <div className="min-w-0">
                    <h2 className="mb-2 text-[clamp(20px,4vw,24px)] font-bold tracking-[-0.025em]">
                      {!waking ? 'Checking your skills…' : 'Waking the server up, the first request takes a few seconds.'}
                    </h2>
                    <p className="mb-5 max-w-[60ch] text-[15px] leading-[1.55] text-ink-2 text-pretty">
                      {!waking
                        ? 'Comparing your skills with 12,872 labelled Indian tech job postings. This usually takes a few seconds.'
                        : 'This can take up to 25 seconds. SkillGraph runs on a free server that sleeps when nobody is using it, so the first check after a quiet spell is slower. Waiting is normal, no need to refresh, and your answers are kept.'}
                    </p>
                    <div className="max-w-[520px]" aria-hidden="true">
                      <div className="h-1.5 bg-accent-track">
                        <div className="h-full bg-accent transition-[width] duration-200 ease-linear" style={{ width: `${Math.min(96, (elapsed / 25) * 100)}%` }} />
                      </div>
                      <div className="mt-2 flex justify-between gap-3 text-[13px] tabular-nums text-ink-3">
                        <span>{Math.floor(elapsed)} s elapsed</span>
                        <span>Cold starts take up to 25 s</span>
                      </div>
                    </div>
                  </div>
                </Card>

                <div aria-hidden="true" className="mb-12 mt-4 flex flex-wrap gap-4">
                  <div className="grid flex-[1.35_1_380px] gap-[22px] border border-line bg-surface p-7">
                    <Skeleton className="h-3 w-[180px]" />
                    <SkeletonBarRow w="44%" />
                    <SkeletonBarRow w="36%" />
                    <SkeletonBarRow w="52%" />
                  </div>
                  <div className="grid flex-[1_1_300px] content-start gap-[22px] border border-line bg-surface p-7">
                    <Skeleton className="h-3 w-[160px]" />
                    <SkeletonBarRow w="44%" tag="h-5 w-11" />
                    <SkeletonBarRow w="36%" tag="h-5 w-11" />
                    <SkeletonBarRow w="52%" tag="h-5 w-11" />
                  </div>
                </div>
              </motion.div>
            )}

            {status === 'error' && error && (
              <Card tone="error" role="alert" className="mb-14 grid grid-cols-[auto_minmax(0,1fr)] gap-4">
                <CircleAlert size={24} strokeWidth={2} className="mt-0.5 text-ink-2" aria-hidden="true" />
                <div className="min-w-0">
                  <h2 className="mb-2 text-[clamp(20px,4vw,24px)] font-bold tracking-[-0.025em]">{error.title || 'Something went wrong'}</h2>
                  <p className="mb-1.5 max-w-[58ch] text-[15px] leading-[1.55] text-ink-2 text-pretty">{error.message}</p>
                  {error.unrecognized?.length > 0 && (
                    <p className="mb-3 text-sm text-ink-3">
                      Unrecognized: <strong className="font-semibold text-ink-2">{error.unrecognized.join(', ')}</strong>. Try checking the spelling or picking suggestions from our list.
                    </p>
                  )}
                  <p className="mb-5 text-sm text-ink-3">
                    Your {shownSkills.length} skills and {shownRole} are still here.
                  </p>
                  <div className="flex flex-wrap gap-2.5">
                    <button type="button" onClick={handleRetry} className={`${primaryBtn} group`}>
                      <RefreshCw size={16} strokeWidth={2} aria-hidden="true" className="transition-transform duration-500 group-hover:rotate-180" />
                      Try again
                    </button>
                    <button type="button" onClick={handleEdit} className={secondaryBtn}>
                      Edit my answers
                    </button>
                  </div>
                </div>
              </Card>
            )}

            {status === 'success' && result && (
              <>
                {unrecognized.length > 0 && (
                  <p className="mb-4 flex items-start gap-2.5 border border-line bg-surface px-4 py-3 text-sm leading-normal text-ink-2">
                    <Info size={16} strokeWidth={2} className="mt-[3px] flex-none" aria-hidden="true" />
                    <span className="[overflow-wrap:anywhere]">
                      We didn't recognise: <strong className="font-semibold text-ink">{unrecognized.join(', ')}</strong>.{' '}
                      {unrecognized.length === 1
                        ? 'It wasn’t counted. Check the spelling or pick from the suggestions.'
                        : 'They weren’t counted. Check the spelling or pick from the suggestions.'}
                    </span>
                  </p>
                )}

                <ReadinessPanel readiness={result.readiness} role={shownRole} topSkills={roleInfo?.top_skills || []} />

                <div className="mt-4 flex flex-wrap items-stretch gap-4">
                  <GapPanel
                    className="flex-[1.35_1_380px]"
                    recommendations={result.gap?.recommendations || []}
                    probability={result.readiness.probability}
                    role={shownRole}
                  />
                  <MatchPanel
                    className="flex-[1_1_300px]"
                    matches={result.match?.matches || []}
                    desiredRole={shownRole}
                    onSwitchRole={handleSwitchRole}
                  />
                </div>

                <RoleSkillMix role={roleInfo} covered={result.readiness.covered || []} />

                <div className="mb-14 mt-7 flex flex-wrap gap-2.5">
                  <motion.button whileTap={{ scale: 0.97 }} type="button" onClick={handleEdit} className={secondaryBtn}>
                    <RotateCcw size={16} strokeWidth={2} aria-hidden="true" className="transition-transform duration-500 group-hover:-rotate-[360deg]" />
                    Analyze again
                  </motion.button>
                </div>
              </>
            )}
          </motion.div>
        )}
        </AnimatePresence>
        <Footer />
      </main>
    </div>
  );
}
