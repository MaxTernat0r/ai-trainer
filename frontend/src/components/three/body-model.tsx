"use client";

import { useMemo, useState } from "react";
import { cn } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface HighlightedMuscle {
  name: string;
  intensity: number; // 0 to 1
}

interface BodyModelProps {
  highlightedMuscles?: HighlightedMuscle[];
  className?: string;
}

type ViewSide = "front" | "back";

// ---------------------------------------------------------------------------
// Muscle group region definitions
// Each muscle maps to an SVG path that roughly outlines its position on the
// body diagram.  The path coordinates use a 200x400 viewBox.
// ---------------------------------------------------------------------------

interface MuscleRegion {
  side: ViewSide;
  path: string;
}

const MUSCLE_REGIONS: Record<string, MuscleRegion> = {
  // --- Front view ---
  chest: {
    side: "front",
    path: "M70,95 Q80,88 100,86 Q120,88 130,95 L135,115 Q120,120 100,122 Q80,120 65,115 Z",
  },
  abs: {
    side: "front",
    path: "M78,122 L122,122 L120,190 Q100,195 80,190 Z",
  },
  obliques: {
    side: "front",
    path: "M65,115 L78,122 L80,190 Q72,185 65,175 Z M135,115 L122,122 L120,190 Q128,185 135,175 Z",
  },
  quads: {
    side: "front",
    path: "M70,200 L90,200 L88,290 Q78,295 70,290 Z M110,200 L130,200 L130,290 Q122,295 112,290 Z",
  },
  front_delts: {
    side: "front",
    path: "M55,82 Q65,75 70,82 L70,100 Q62,105 55,100 Z M130,82 Q135,75 145,82 L145,100 Q138,105 130,100 Z",
  },
  biceps: {
    side: "front",
    path: "M45,105 L55,100 L58,150 Q50,155 43,150 Z M145,100 L155,105 L157,150 Q150,155 142,150 Z",
  },
  forearms: {
    side: "front",
    path: "M40,155 L55,150 L50,210 Q44,212 38,208 Z M145,150 L160,155 L162,208 Q156,212 150,210 Z",
  },
  hip_flexors: {
    side: "front",
    path: "M80,190 Q90,198 100,200 Q110,198 120,190 L120,205 Q100,210 80,205 Z",
  },
  tibialis: {
    side: "front",
    path: "M72,295 L88,290 L85,350 Q78,352 72,348 Z M112,290 L128,295 L128,348 Q122,352 115,350 Z",
  },

  // --- Back view ---
  traps: {
    side: "back",
    path: "M80,72 Q90,68 100,66 Q110,68 120,72 L125,92 Q112,88 100,86 Q88,88 75,92 Z",
  },
  rear_delts: {
    side: "back",
    path: "M55,82 Q65,75 70,82 L70,100 Q62,105 55,100 Z M130,82 Q135,75 145,82 L145,100 Q138,105 130,100 Z",
  },
  lats: {
    side: "back",
    path: "M65,95 L78,92 L80,155 Q72,160 62,150 Z M122,92 L135,95 L138,150 Q128,160 120,155 Z",
  },
  lower_back: {
    side: "back",
    path: "M78,155 L122,155 L120,192 Q100,198 80,192 Z",
  },
  triceps: {
    side: "back",
    path: "M45,105 L55,100 L58,155 Q50,160 43,155 Z M145,100 L155,105 L157,155 Q150,160 142,155 Z",
  },
  glutes: {
    side: "back",
    path: "M70,192 L130,192 L132,225 Q115,235 100,236 Q85,235 68,225 Z",
  },
  hamstrings: {
    side: "back",
    path: "M70,228 L90,235 L88,310 Q78,315 70,308 Z M110,235 L130,228 L130,308 Q122,315 112,310 Z",
  },
  calves: {
    side: "back",
    path: "M72,312 L88,310 L85,365 Q78,368 72,364 Z M112,310 L128,312 L128,364 Q122,368 115,365 Z",
  },
  rhomboids: {
    side: "back",
    path: "M82,92 L100,86 L118,92 L115,120 Q100,116 85,120 Z",
  },
};

// ---------------------------------------------------------------------------
// Map common muscle name variations to our region keys
// ---------------------------------------------------------------------------

const MUSCLE_ALIASES: Record<string, string> = {
  pecs: "chest",
  pectorals: "chest",
  pectoralis: "chest",
  abdominals: "abs",
  core: "abs",
  quadriceps: "quads",
  "front deltoids": "front_delts",
  "anterior deltoids": "front_delts",
  shoulders: "front_delts",
  deltoids: "front_delts",
  delts: "front_delts",
  "rear deltoids": "rear_delts",
  "posterior deltoids": "rear_delts",
  "upper back": "traps",
  trapezius: "traps",
  latissimus: "lats",
  "latissimus dorsi": "lats",
  back: "lats",
  "lower back": "lower_back",
  erectors: "lower_back",
  "spinal erectors": "lower_back",
  glutes: "glutes",
  gluteus: "glutes",
  "gluteus maximus": "glutes",
  hamstring: "hamstrings",
  "biceps femoris": "hamstrings",
  calf: "calves",
  gastrocnemius: "calves",
  soleus: "calves",
  bicep: "biceps",
  "biceps brachii": "biceps",
  tricep: "triceps",
  "triceps brachii": "triceps",
  forearm: "forearms",
  "wrist flexors": "forearms",
  oblique: "obliques",
  "external obliques": "obliques",
  "hip flexor": "hip_flexors",
  iliopsoas: "hip_flexors",
  "shin muscles": "tibialis",
  "tibialis anterior": "tibialis",
  rhomboid: "rhomboids",
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Interpolate from light yellow to deep red based on intensity (0-1). */
function intensityToColor(intensity: number): string {
  const clamped = Math.max(0, Math.min(1, intensity));

  // Light yellow: hsl(50, 100%, 80%)  ->  Deep red: hsl(0, 85%, 45%)
  const h = 50 - clamped * 50; // 50 -> 0
  const s = 100 - clamped * 15; // 100 -> 85
  const l = 80 - clamped * 35; // 80 -> 45

  return `hsl(${Math.round(h)}, ${Math.round(s)}%, ${Math.round(l)}%)`;
}

function resolveMuscleKey(name: string): string | undefined {
  const lower = name.toLowerCase().replace(/[-_]/g, "_");
  if (MUSCLE_REGIONS[lower]) return lower;
  if (MUSCLE_ALIASES[lower]) return MUSCLE_ALIASES[lower];

  // Fuzzy: check if the name is a substring of a key or vice versa
  for (const key of Object.keys(MUSCLE_REGIONS)) {
    if (key.includes(lower) || lower.includes(key)) return key;
  }
  for (const [alias, key] of Object.entries(MUSCLE_ALIASES)) {
    if (alias.includes(lower) || lower.includes(alias)) return key;
  }

  return undefined;
}

// ---------------------------------------------------------------------------
// SVG body outline
// ---------------------------------------------------------------------------

function BodyOutlineFront() {
  return (
    <g
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      fill="none"
      className="text-muted-foreground/50"
    >
      {/* Head */}
      <ellipse cx="100" cy="30" rx="18" ry="22" />
      {/* Neck */}
      <line x1="92" y1="52" x2="92" y2="66" />
      <line x1="108" y1="52" x2="108" y2="66" />
      {/* Shoulders */}
      <path d="M92,66 Q80,66 65,72 Q50,80 50,100" />
      <path d="M108,66 Q120,66 135,72 Q150,80 150,100" />
      {/* Torso sides */}
      <line x1="65" y1="95" x2="68" y2="195" />
      <line x1="135" y1="95" x2="132" y2="195" />
      {/* Arms left */}
      <path d="M50,100 Q42,130 38,155 Q34,180 30,210" />
      <path d="M58,100 Q52,130 48,155 Q44,180 40,210" />
      {/* Arms right */}
      <path d="M150,100 Q158,130 162,155 Q166,180 170,210" />
      <path d="M142,100 Q148,130 152,155 Q156,180 160,210" />
      {/* Waist to hips */}
      <path d="M68,195 Q80,205 100,208 Q120,205 132,195" />
      {/* Legs */}
      <path d="M80,205 Q76,250 74,290 Q72,320 68,365" />
      <path d="M96,208 Q94,250 92,290 Q90,320 88,365" />
      <path d="M104,208 Q106,250 108,290 Q110,320 112,365" />
      <path d="M120,205 Q124,250 126,290 Q128,320 132,365" />
      {/* Feet */}
      <path d="M68,365 Q65,372 62,375 Q72,378 88,375 Q88,370 88,365" />
      <path d="M112,365 Q112,370 112,375 Q128,378 138,375 Q135,372 132,365" />
    </g>
  );
}

function BodyOutlineBack() {
  return (
    <g
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      fill="none"
      className="text-muted-foreground/50"
    >
      {/* Head */}
      <ellipse cx="100" cy="30" rx="18" ry="22" />
      {/* Neck */}
      <line x1="92" y1="52" x2="92" y2="66" />
      <line x1="108" y1="52" x2="108" y2="66" />
      {/* Shoulders */}
      <path d="M92,66 Q80,66 65,72 Q50,80 50,100" />
      <path d="M108,66 Q120,66 135,72 Q150,80 150,100" />
      {/* Torso sides */}
      <line x1="65" y1="95" x2="68" y2="195" />
      <line x1="135" y1="95" x2="132" y2="195" />
      {/* Arms left */}
      <path d="M50,100 Q42,130 38,155 Q34,180 30,210" />
      <path d="M58,100 Q52,130 48,155 Q44,180 40,210" />
      {/* Arms right */}
      <path d="M150,100 Q158,130 162,155 Q166,180 170,210" />
      <path d="M142,100 Q148,130 152,155 Q156,180 160,210" />
      {/* Waist to hips */}
      <path d="M68,195 Q80,205 100,208 Q120,205 132,195" />
      {/* Legs */}
      <path d="M80,205 Q76,250 74,290 Q72,320 68,365" />
      <path d="M96,208 Q94,250 92,290 Q90,320 88,365" />
      <path d="M104,208 Q106,250 108,290 Q110,320 112,365" />
      <path d="M120,205 Q124,250 126,290 Q128,320 132,365" />
      {/* Feet */}
      <path d="M68,365 Q65,372 62,375 Q72,378 88,375 Q88,370 88,365" />
      <path d="M112,365 Q112,370 112,375 Q128,378 138,375 Q135,372 132,365" />
      {/* Spine line (back only) */}
      <line
        x1="100"
        y1="66"
        x2="100"
        y2="195"
        strokeDasharray="4 3"
        className="text-muted-foreground/25"
      />
    </g>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function BodyModel({ highlightedMuscles = [], className }: BodyModelProps) {
  const [viewSide, setViewSide] = useState<ViewSide>("front");

  // Build a lookup: regionKey -> color
  const highlightMap = useMemo(() => {
    const map = new Map<string, string>();
    for (const { name, intensity } of highlightedMuscles) {
      const key = resolveMuscleKey(name);
      if (key) {
        map.set(key, intensityToColor(intensity));
      }
    }
    return map;
  }, [highlightedMuscles]);

  // Determine which regions to render for the current view side
  const visibleRegions = useMemo(() => {
    return Object.entries(MUSCLE_REGIONS)
      .filter(([, region]) => region.side === viewSide)
      .map(([key, region]) => ({
        key,
        path: region.path,
        color: highlightMap.get(key),
      }));
  }, [viewSide, highlightMap]);

  return (
    <div className={cn("flex flex-col items-center gap-3", className)}>
      {/* Front / Back toggle */}
      <div className="inline-flex rounded-lg border bg-muted p-0.5 text-sm">
        <button
          type="button"
          onClick={() => setViewSide("front")}
          className={cn(
            "rounded-md px-3 py-1 transition-colors",
            viewSide === "front"
              ? "bg-background font-medium text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground",
          )}
        >
          Front
        </button>
        <button
          type="button"
          onClick={() => setViewSide("back")}
          className={cn(
            "rounded-md px-3 py-1 transition-colors",
            viewSide === "back"
              ? "bg-background font-medium text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground",
          )}
        >
          Back
        </button>
      </div>

      {/* SVG body diagram */}
      <svg
        viewBox="0 0 200 400"
        className="h-full max-h-[420px] w-auto"
        role="img"
        aria-label={`Body muscle diagram - ${viewSide} view`}
      >
        {/* Highlighted muscle regions */}
        {visibleRegions.map(({ key, path, color }) => (
          <path
            key={key}
            d={path}
            fill={color ?? "transparent"}
            stroke={color ? "rgba(0,0,0,0.15)" : "none"}
            strokeWidth="0.5"
            opacity={color ? 0.8 : 0}
            className="transition-all duration-300"
          >
            <title>{key.replace(/_/g, " ")}</title>
          </path>
        ))}

        {/* Body outline on top */}
        {viewSide === "front" ? <BodyOutlineFront /> : <BodyOutlineBack />}
      </svg>

      {/* Legend */}
      {highlightedMuscles.length > 0 && (
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <span
              className="inline-block h-3 w-3 rounded-sm"
              style={{ background: intensityToColor(0.2) }}
            />
            <span>Low</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span
              className="inline-block h-3 w-3 rounded-sm"
              style={{ background: intensityToColor(0.6) }}
            />
            <span>Medium</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span
              className="inline-block h-3 w-3 rounded-sm"
              style={{ background: intensityToColor(1.0) }}
            />
            <span>High</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default BodyModel;
