import * as React from "react"

import { cn } from "@/lib/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "file:text-foreground placeholder:text-muted-foreground/75 selection:bg-primary selection:text-primary-foreground border-[rgb(var(--theme-shade-rgb)/58%)] h-11 w-full min-w-0 rounded-lg border bg-[linear-gradient(180deg,rgb(255_255_255_/_4%),rgb(255_255_255_/_1%)),rgb(0_0_0_/_24%)] px-3.5 py-2 text-base shadow-[inset_0_1px_0_rgb(255_255_255_/_6%),inset_0_0_18px_rgb(var(--brand-deep-bg)/_30%)] backdrop-blur-xl transition-[border-color,background-color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
        "focus-visible:border-[rgb(var(--brand-edge)/80%)] focus-visible:bg-[linear-gradient(180deg,rgb(255_255_255_/_6%),rgb(255_255_255_/_2%)),rgb(var(--brand-deep-bg)/_50%)] focus-visible:ring-primary/18 focus-visible:ring-[3px] focus-visible:shadow-[inset_0_1px_0_rgb(255_255_255_/_8%),0_0_24px_rgb(var(--brand-shade)/_18%)]",
        "aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
        className
      )}
      {...props}
    />
  )
}

export { Input }
