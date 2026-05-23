import * as React from "react"

import { cn } from "@/lib/utils"

function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        "border-[rgb(var(--theme-shade-rgb)/58%)] placeholder:text-muted-foreground/75 focus-visible:border-[#a12d42]/80 focus-visible:bg-[linear-gradient(180deg,rgb(255_255_255_/_6%),rgb(255_255_255_/_2%)),rgb(42_8_15_/_42%)] focus-visible:ring-primary/18 aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive flex field-sizing-content min-h-24 w-full rounded-lg border bg-[linear-gradient(180deg,rgb(255_255_255_/_4%),rgb(255_255_255_/_1%)),rgb(0_0_0_/_24%)] px-3.5 py-3 text-base shadow-[inset_0_1px_0_rgb(255_255_255_/_6%),inset_0_0_18px_rgb(74_11_21_/_10%)] backdrop-blur-xl transition-[border-color,background-color,box-shadow] outline-none focus-visible:ring-[3px] focus-visible:shadow-[inset_0_1px_0_rgb(255_255_255_/_8%),0_0_24px_rgb(118_24_38_/_18%)] disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
        className
      )}
      {...props}
    />
  )
}

export { Textarea }
