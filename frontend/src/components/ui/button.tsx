import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { Slot } from "radix-ui"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "relative isolate inline-flex items-center justify-center gap-2 overflow-hidden whitespace-nowrap rounded-lg text-sm font-semibold transition-all duration-200 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
  {
    variants: {
      variant: {
        default: "border border-[#712031]/75 bg-[linear-gradient(180deg,rgb(255_255_255_/_7%),rgb(255_255_255_/_2%)),linear-gradient(120deg,rgb(8_8_12_/_96%),rgb(42_8_15_/_80%))] text-primary-foreground shadow-[inset_0_1px_0_rgb(255_255_255_/_10%),inset_0_0_22px_rgb(96_14_26_/_14%),0_0_22px_rgb(118_24_38_/_18%)] hover:border-[#a12d42]/85 hover:bg-[linear-gradient(180deg,rgb(255_255_255_/_9%),rgb(255_255_255_/_3%)),linear-gradient(120deg,rgb(12_12_16_/_96%),rgb(56_10_19_/_82%))] hover:shadow-[inset_0_1px_0_rgb(255_255_255_/_12%),inset_0_0_26px_rgb(96_14_26_/_18%),0_0_30px_rgb(118_24_38_/_26%)] active:scale-[0.99]",
        destructive:
          "border border-destructive/50 bg-[linear-gradient(180deg,rgb(124_27_36),rgb(52_8_14))] text-white shadow-[inset_0_1px_0_rgb(255_255_255_/_10%),0_0_22px_rgb(124_27_36_/_18%)] hover:border-destructive/75 hover:bg-[linear-gradient(180deg,rgb(142_32_43),rgb(68_10_18))] focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40",
        outline:
          "border border-[#712031]/58 bg-[linear-gradient(180deg,rgb(255_255_255_/_4%),rgb(255_255_255_/_1%)),rgb(0_0_0_/_22%)] shadow-[inset_0_1px_0_rgb(255_255_255_/_6%)] backdrop-blur-xl hover:border-[#9a3045]/78 hover:bg-[linear-gradient(180deg,rgb(255_255_255_/_6%),rgb(255_255_255_/_2%)),rgb(42_8_15_/_36%)] hover:text-foreground hover:shadow-[inset_0_1px_0_rgb(255_255_255_/_8%),0_0_22px_rgb(118_24_38_/_16%)]",
        secondary:
          "border border-white/12 bg-[linear-gradient(180deg,rgb(255_255_255_/_7%),rgb(255_255_255_/_2%)),rgb(255_255_255_/_4%)] text-secondary-foreground shadow-[inset_0_1px_0_rgb(255_255_255_/_8%)] hover:border-[#712031]/58 hover:bg-secondary/70",
        ghost:
          "border border-transparent bg-transparent hover:border-[#712031]/55 hover:bg-white/8 hover:text-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2 has-[>svg]:px-3",
        xs: "h-6 gap-1 rounded-md px-2 text-xs has-[>svg]:px-1.5 [&_svg:not([class*='size-'])]:size-3",
        sm: "h-8 rounded-lg gap-1.5 px-3 has-[>svg]:px-2.5",
        lg: "h-11 rounded-lg px-6 has-[>svg]:px-4",
        icon: "size-10",
        "icon-xs": "size-6 rounded-md [&_svg:not([class*='size-'])]:size-3",
        "icon-sm": "size-8 rounded-lg",
        "icon-lg": "size-11 rounded-lg",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant = "default",
  size = "default",
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot.Root : "button"

  return (
    <Comp
      data-slot="button"
      data-variant={variant}
      data-size={size}
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
