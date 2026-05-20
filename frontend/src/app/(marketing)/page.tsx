import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  return (
    <section className="fixed inset-0 z-10 flex items-center justify-center overflow-hidden px-4">
      <div className="flex w-full max-w-2xl flex-col items-center text-center">
        <div className="mb-4 flex flex-wrap justify-center gap-2">
          <span className="status-pill">Coach AI</span>
          <span className="status-pill">спортивный менеджер</span>
        </div>

        <h1 className="text-[2rem] font-semibold leading-[1.05] sm:text-5xl xl:text-6xl">
          Личный спортивный менеджер
        </h1>

        <p className="mt-3 max-w-xl text-sm leading-6 text-muted-foreground sm:mt-4 sm:text-lg sm:leading-7">
          Coach AI превращает цель в понятную систему: тренировки, питание,
          нагрузка, восстановление и прогресс в одном маршруте.
        </p>

        <Button size="lg" asChild className="neon-action mt-6 w-full max-w-xs sm:mt-8">
          <Link href="/register">
            <span className="relative z-10 flex items-center gap-2">
              Собрать личный план
              <ArrowRight className="size-4" />
            </span>
          </Link>
        </Button>
      </div>
    </section>
  );
}
