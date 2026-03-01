"use client";

import React, { Suspense, useEffect, useMemo, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, useGLTF, Center, Html } from "@react-three/drei";
import * as THREE from "three";
import { cn } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ExerciseViewerProps {
  modelKey?: string;
  primaryMuscles?: string[];
  secondaryMuscles?: string[];
  autoRotate?: boolean;
  className?: string;
}

interface MuscleModelProps {
  url: string;
  primaryMuscles: string[];
  secondaryMuscles: string[];
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const PRIMARY_COLOR = new THREE.Color("#ff4444");
const SECONDARY_COLOR = new THREE.Color("#ff8844");
const NEUTRAL_COLOR = new THREE.Color("#a0a0a0");

// ---------------------------------------------------------------------------
// Loading spinner shown inside the Canvas while the model is loading
// ---------------------------------------------------------------------------

function CanvasLoader() {
  return (
    <Html center>
      <div className="flex flex-col items-center gap-2">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-muted border-t-primary" />
        <span className="text-xs text-muted-foreground">Loading model...</span>
      </div>
    </Html>
  );
}

// ---------------------------------------------------------------------------
// The inner Three.js scene that loads the GLB and applies muscle highlights
// ---------------------------------------------------------------------------

function MuscleModel({ url, primaryMuscles, secondaryMuscles }: MuscleModelProps) {
  const gltf = useGLTF(url);
  const scene = gltf.scene;

  // Normalise muscle names to lowercase for matching
  const primarySet = useMemo(
    () => new Set(primaryMuscles.map((m) => m.toLowerCase())),
    [primaryMuscles],
  );
  const secondarySet = useMemo(
    () => new Set(secondaryMuscles.map((m) => m.toLowerCase())),
    [secondaryMuscles],
  );

  // Clone the scene so we don't mutate the cached original
  const clonedScene = useMemo(() => scene.clone(true), [scene]);

  // Traverse and apply materials based on mesh name
  useEffect(() => {
    clonedScene.traverse((child) => {
      if (!(child instanceof THREE.Mesh)) return;

      const name = child.name.toLowerCase();

      let color = NEUTRAL_COLOR;
      if (primarySet.has(name)) {
        color = PRIMARY_COLOR;
      } else if (secondarySet.has(name)) {
        color = SECONDARY_COLOR;
      } else {
        // Also check if the mesh name *contains* a muscle name (partial match)
        for (const muscle of primarySet) {
          if (name.includes(muscle) || muscle.includes(name)) {
            color = PRIMARY_COLOR;
            break;
          }
        }
        if (color === NEUTRAL_COLOR) {
          for (const muscle of secondarySet) {
            if (name.includes(muscle) || muscle.includes(name)) {
              color = SECONDARY_COLOR;
              break;
            }
          }
        }
      }

      // Create a new material so we don't mutate shared materials
      child.material = new THREE.MeshStandardMaterial({
        color,
        roughness: 0.6,
        metalness: 0.1,
        transparent: color === NEUTRAL_COLOR,
        opacity: color === NEUTRAL_COLOR ? 0.85 : 1,
      });
    });
  }, [clonedScene, primarySet, secondarySet]);

  return (
    <Center>
      <primitive object={clonedScene} />
    </Center>
  );
}

// ---------------------------------------------------------------------------
// 2D SVG fallback when no model is available or loading fails
// ---------------------------------------------------------------------------

function FallbackPlaceholder({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "flex items-center justify-center rounded-lg border border-dashed border-muted-foreground/25 bg-muted/30",
        className,
      )}
    >
      <svg
        viewBox="0 0 200 350"
        className="h-full max-h-64 w-auto text-muted-foreground/40"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {/* Head */}
        <circle cx="100" cy="35" r="22" />
        {/* Neck */}
        <line x1="100" y1="57" x2="100" y2="72" />
        {/* Torso */}
        <line x1="100" y1="72" x2="100" y2="185" />
        {/* Shoulders */}
        <line x1="100" y1="90" x2="55" y2="100" />
        <line x1="100" y1="90" x2="145" y2="100" />
        {/* Left arm */}
        <line x1="55" y1="100" x2="40" y2="155" />
        <line x1="40" y1="155" x2="35" y2="210" />
        {/* Right arm */}
        <line x1="145" y1="100" x2="160" y2="155" />
        <line x1="160" y1="155" x2="165" y2="210" />
        {/* Hips */}
        <line x1="100" y1="185" x2="70" y2="200" />
        <line x1="100" y1="185" x2="130" y2="200" />
        {/* Left leg */}
        <line x1="70" y1="200" x2="65" y2="275" />
        <line x1="65" y1="275" x2="60" y2="340" />
        {/* Right leg */}
        <line x1="130" y1="200" x2="135" y2="275" />
        <line x1="135" y1="275" x2="140" y2="340" />
      </svg>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Error boundary for catching Three.js render errors
// ---------------------------------------------------------------------------

interface ErrorBoundaryState {
  hasError: boolean;
}

class ViewerErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback: React.ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: React.ReactNode; fallback: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}

// ---------------------------------------------------------------------------
// Main exported component
// ---------------------------------------------------------------------------

export function ExerciseViewer({
  modelKey,
  primaryMuscles = [],
  secondaryMuscles = [],
  autoRotate = true,
  className,
}: ExerciseViewerProps) {
  const [modelFailed, setModelFailed] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const modelUrl = modelKey ? `/models/${modelKey}.glb` : null;

  // Pre-check: attempt to fetch the model head to see if it exists.
  // This avoids a flash of error inside the Canvas.
  useEffect(() => {
    if (!modelUrl) return;

    let cancelled = false;

    fetch(modelUrl, { method: "HEAD" })
      .then((res) => {
        if (!cancelled && !res.ok) setModelFailed(true);
      })
      .catch(() => {
        if (!cancelled) setModelFailed(true);
      });

    return () => {
      cancelled = true;
    };
  }, [modelUrl]);

  // Render fallback when there is no model key or the model failed to load
  if (!modelUrl || modelFailed) {
    return <FallbackPlaceholder className={cn("h-full min-h-[240px] w-full", className)} />;
  }

  return (
    <div ref={containerRef} className={cn("relative h-full min-h-[240px] w-full", className)}>
      <ViewerErrorBoundary
        fallback={<FallbackPlaceholder className="h-full w-full" />}
      >
        <Canvas
          camera={{ position: [0, 1, 3], fov: 50 }}
          className="!absolute inset-0"
          gl={{ antialias: true, alpha: true }}
          dpr={[1, 2]}
        >
          {/* Lighting */}
          <ambientLight intensity={0.6} />
          <directionalLight position={[5, 5, 5]} intensity={0.8} castShadow />
          <directionalLight position={[-3, 3, -3]} intensity={0.3} />

          {/* Controls */}
          <OrbitControls
            autoRotate={autoRotate}
            autoRotateSpeed={1.5}
            enablePan={false}
            minDistance={1.5}
            maxDistance={6}
            maxPolarAngle={Math.PI * 0.85}
          />

          {/* Model with suspense */}
          <Suspense fallback={<CanvasLoader />}>
            <MuscleModel
              url={modelUrl}
              primaryMuscles={primaryMuscles}
              secondaryMuscles={secondaryMuscles}
            />
          </Suspense>
        </Canvas>
      </ViewerErrorBoundary>
    </div>
  );
}

export default ExerciseViewer;
