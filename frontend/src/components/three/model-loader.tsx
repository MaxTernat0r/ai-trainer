"use client";

import dynamic from "next/dynamic";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import type { ComponentProps } from "react";

// ---------------------------------------------------------------------------
// Dynamically import the ExerciseViewer with SSR disabled.
// Three.js and WebGL require browser APIs that are not available on the server.
// ---------------------------------------------------------------------------

const ExerciseViewerLazy = dynamic(
  () => import("@/components/three/exercise-viewer").then((mod) => mod.ExerciseViewer),
  {
    ssr: false,
    loading: () => <ModelLoaderSkeleton />,
  },
);

// ---------------------------------------------------------------------------
// Loading skeleton
// ---------------------------------------------------------------------------

function ModelLoaderSkeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "flex h-full min-h-[240px] w-full flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-muted-foreground/25 bg-muted/20 p-4",
        className,
      )}
    >
      {/* Simulated body shape skeleton */}
      <Skeleton className="h-6 w-6 rounded-full" />
      <Skeleton className="h-20 w-14 rounded-md" />
      <Skeleton className="h-24 w-16 rounded-md" />
      <span className="text-xs text-muted-foreground">Loading 3D viewer...</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Re-export with identical props
// ---------------------------------------------------------------------------

type ExerciseViewerProps = ComponentProps<typeof ExerciseViewerLazy>;

export function ModelLoader(props: ExerciseViewerProps) {
  return <ExerciseViewerLazy {...props} />;
}

export { ModelLoaderSkeleton };
export default ModelLoader;
