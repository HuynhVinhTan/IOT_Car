import { useEffect, useRef } from "react";

const BEEP_INTERVAL_MS = 900;
const BEEP_FREQUENCY_HZ = 880;
const BEEP_DURATION_S = 0.18;
const BEEP_VOLUME = 0.12;

export function usePersonDetectionAlert(active: boolean) {
  const audioContextRef = useRef<AudioContext | null>(null);
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    if (!active) {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      if (audioContextRef.current) {
        void audioContextRef.current.close();
        audioContextRef.current = null;
      }
      return;
    }

    const playBeep = () => {
      const context = audioContextRef.current;
      if (!context) {
        return;
      }

      const oscillator = context.createOscillator();
      const gain = context.createGain();
      oscillator.type = "square";
      oscillator.frequency.value = BEEP_FREQUENCY_HZ;
      gain.gain.setValueAtTime(BEEP_VOLUME, context.currentTime);
      gain.gain.exponentialRampToValueAtTime(
        0.001,
        context.currentTime + BEEP_DURATION_S
      );
      oscillator.connect(gain);
      gain.connect(context.destination);
      oscillator.start(context.currentTime);
      oscillator.stop(context.currentTime + BEEP_DURATION_S);
    };

    const startAlert = async () => {
      if (!audioContextRef.current) {
        audioContextRef.current = new AudioContext();
      }

      try {
        await audioContextRef.current.resume();
      } catch {
        return;
      }

      playBeep();
      intervalRef.current = window.setInterval(playBeep, BEEP_INTERVAL_MS);
    };

    const unlockAudio = () => {
      void startAlert();
      document.removeEventListener("pointerdown", unlockAudio);
      document.removeEventListener("keydown", unlockAudio);
    };

    document.addEventListener("pointerdown", unlockAudio);
    document.addEventListener("keydown", unlockAudio);
    void startAlert();

    return () => {
      document.removeEventListener("pointerdown", unlockAudio);
      document.removeEventListener("keydown", unlockAudio);
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      if (audioContextRef.current) {
        void audioContextRef.current.close();
        audioContextRef.current = null;
      }
    };
  }, [active]);
}
