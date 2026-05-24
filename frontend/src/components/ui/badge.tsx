import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { Slot } from "radix-ui"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center justify-center rounded-full border border-transparent px-2.5 py-0.5 text-[0.68rem] font-bold uppercase tracking-[0.08em] w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1.5 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,border-color,background-color,box-shadow] overflow-hidden",
  {
    variants: {
      variant: {
        default: "border-[rgb(var(--brand-edge)/65%)] bg-[rgb(var(--brand-deep-bg)/70%)] text-zinc-100 shadow-[0_0_18px_rgb(var(--brand-shade)/_18%)] [a&]:hover:bg-[rgb(var(--brand-deep-bg)/85%)]",
        secondary:
          "border-[rgb(var(--theme-shade-rgb)/50%)] bg-white/[0.045] text-secondary-foreground [a&]:hover:bg-white/10",
        destructive:
          "border-destructive/40 bg-destructive/14 text-red-200 [a&]:hover:bg-destructive/20 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40",
        outline:
          "border-[rgb(var(--theme-shade-rgb)/55%)] bg-white/[0.025] text-foreground/85 [a&]:hover:border-[rgb(var(--brand-edge)/75%)] [a&]:hover:bg-[rgb(var(--brand-deep-bg)/40%)] [a&]:hover:text-foreground",
        ghost: "[a&]:hover:bg-accent [a&]:hover:text-accent-foreground",
        link: "text-primary underline-offset-4 [a&]:hover:underline",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

function Badge({
  className,
  variant = "default",
  asChild = false,
  ...props
}: React.ComponentProps<"span"> &
  VariantProps<typeof badgeVariants> & { asChild?: boolean }) {
  const Comp = asChild ? Slot.Root : "span"

  return (
    <Comp
      data-slot="badge"
      data-variant={variant}
      className={cn(badgeVariants({ variant }), className)}
      {...props}
    />
  )
}

export { Badge, badgeVariants }
