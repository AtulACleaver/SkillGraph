import { useEffect, useRef, useState } from 'react';

export function useReveal({ threshold = 0.1, rootMargin = '0px', triggerOnce = true } = {}) {
  const [isRevealed, setIsRevealed] = useState(
    () =>
      typeof window !== 'undefined' &&
      (window.matchMedia('(prefers-reduced-motion: reduce)').matches || typeof IntersectionObserver === 'undefined')
  );
  const ref = useRef(null);

  useEffect(() => {
    if (isRevealed || typeof IntersectionObserver === 'undefined') return;

    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsRevealed(true);
          if (triggerOnce) observer.unobserve(el);
        } else if (!triggerOnce) {
          setIsRevealed(false);
        }
      },
      { threshold, rootMargin }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [threshold, rootMargin, triggerOnce, isRevealed]);

  return [ref, isRevealed];
}
