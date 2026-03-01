'use client';

import { useState, useRef, useCallback, useEffect } from 'react';

interface UseTimerReturn {
  seconds: number;
  isRunning: boolean;
  start: (durationSecs: number) => void;
  pause: () => void;
  reset: () => void;
}

function notifyTimerComplete() {
  // Vibrate if supported
  if (typeof navigator !== 'undefined' && 'vibrate' in navigator) {
    navigator.vibrate([200, 100, 200]);
  }

  // Play a notification sound
  try {
    const audioCtx = new AudioContext();
    const oscillator = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    oscillator.connect(gain);
    gain.connect(audioCtx.destination);
    oscillator.frequency.value = 880;
    oscillator.type = 'sine';
    gain.gain.value = 0.3;
    oscillator.start();
    oscillator.stop(audioCtx.currentTime + 0.3);
  } catch {
    // Audio not available — silently ignore
  }
}

export function useTimer(): UseTimerReturn {
  const [seconds, setSeconds] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const hasNotifiedRef = useRef(false);

  const clearTimer = useCallback(() => {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const start = useCallback(
    (durationSecs: number) => {
      clearTimer();
      setSeconds(durationSecs);
      setIsRunning(true);
      hasNotifiedRef.current = false;

      intervalRef.current = setInterval(() => {
        setSeconds((prev) => {
          if (prev <= 1) {
            clearTimer();
            setIsRunning(false);
            if (!hasNotifiedRef.current) {
              hasNotifiedRef.current = true;
              notifyTimerComplete();
            }
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    },
    [clearTimer]
  );

  const pause = useCallback(() => {
    clearTimer();
    setIsRunning(false);
  }, [clearTimer]);

  const reset = useCallback(() => {
    clearTimer();
    setSeconds(0);
    setIsRunning(false);
    hasNotifiedRef.current = false;
  }, [clearTimer]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearTimer();
    };
  }, [clearTimer]);

  return { seconds, isRunning, start, pause, reset };
}
