import { useEffect, useState } from 'react';

function easeOutExpo(x) {
  return x === 1 ? 1 : 1 - Math.pow(2, -10 * x);
}

export function useCountUp(end, durationMs = 1000, start = 0) {
  const [count, setCount] = useState(start);

  const prefersReducedMotion =
    typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const shouldSkip = prefersReducedMotion || durationMs === 0;

  useEffect(() => {
    if (shouldSkip) return;

    let startTime = null;
    let animationFrameId;

    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = timestamp - startTime;
      const percentage = Math.min(progress / durationMs, 1);
      
      const easedProgress = easeOutExpo(percentage);
      const currentCount = Math.round(easedProgress * (end - start) + start);
      
      setCount(currentCount);

      if (progress < durationMs) {
        animationFrameId = window.requestAnimationFrame(animate);
      } else {
        setCount(end); // ensure we hit the exact end value
      }
    };

    animationFrameId = window.requestAnimationFrame(animate);

    return () => {
      if (animationFrameId) {
        window.cancelAnimationFrame(animationFrameId);
      }
    };
  }, [end, durationMs, start, shouldSkip]);

  return shouldSkip ? end : count;
}
