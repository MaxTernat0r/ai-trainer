'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Palette = 'crimson' | 'aurora';

interface PaletteState {
  palette: Palette;
  cyclePalette: () => void;
  setPalette: (p: Palette) => void;
}

const PALETTE_CLASS: Record<Palette, string> = {
  crimson: 'theme-crimson',
  aurora: 'theme-aurora',
};

const ALL_PALETTE_CLASSES = Object.values(PALETTE_CLASS);

function applyPaletteToDom(p: Palette) {
  if (typeof document === 'undefined') return;
  const html = document.documentElement;
  for (const cls of ALL_PALETTE_CLASSES) {
    html.classList.remove(cls);
  }
  html.classList.add(PALETTE_CLASS[p]);

  // Retrigger entrance animations
  html.removeAttribute('data-theme-flash');
  // Force reflow so the next add restarts animations
  void html.offsetHeight;
  html.setAttribute('data-theme-flash', '1');
  window.setTimeout(() => {
    html.removeAttribute('data-theme-flash');
  }, 760);
}

export const usePaletteStore = create<PaletteState>()(
  persist(
    (set, get) => ({
      palette: 'crimson',
      cyclePalette: () => {
        const next: Palette = get().palette === 'crimson' ? 'aurora' : 'crimson';
        applyPaletteToDom(next);
        set({ palette: next });
      },
      setPalette: (p) => {
        applyPaletteToDom(p);
        set({ palette: p });
      },
    }),
    {
      name: 'coach-palette',
      onRehydrateStorage: () => (state) => {
        if (state) applyPaletteToDom(state.palette);
      },
    }
  )
);
