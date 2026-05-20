import Link from "next/link";
import {
  ArrowRight,
  Dumbbell,
  LineChart,
  MessageSquare,
  ShieldCheck,
  Target,
  UtensilsCrossed,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const productCards = [
  {
    icon: Dumbbell,
    title: "Тренировочный план",
    text: "Coach AI собирает программу под цель, уровень, график и доступное оборудование.",
  },
  {
    icon: LineChart,
    title: "Мониторинг",
    text: "На данных тренировок, веса, питания и восстановления строятся графики нагрузки и прогресса.",
  },
  {
    icon: UtensilsCrossed,
    title: "Питание и вес",
    text: "Калории, белки и динамика веса становятся частью общего спортивного плана.",
  },
  {
    icon: MessageSquare,
    title: "ИИ-тренер",
    text: "Можно уточнить технику, заменить упражнение или адаптировать план под состояние.",
  },
];

const productFlow = [
  ["01", "цель", "Coach AI понимает задачу и стартовые данные"],
  ["02", "план", "формирует тренировки, питание и контрольные точки"],
  ["03", "адаптация", "корректирует рекомендации по фактическому прогрессу"],
];

export default function LandingPage() {
  return (
    <div className="h-full overflow-hidden">
      <section className="relative z-10 mx-auto grid h-full max-w-7xl grid-rows-[auto_minmax(0,1fr)] gap-2 overflow-hidden px-4 py-3 sm:gap-3 sm:px-6 sm:py-5 lg:grid-cols-[0.82fr_1.18fr] lg:grid-rows-1 lg:items-center lg:gap-6 lg:px-8">
        <div className="relative z-10 flex min-h-0 flex-col justify-center overflow-hidden text-center lg:text-left">
          <div className="mb-2 flex flex-wrap justify-center gap-2 sm:mb-3 lg:justify-start">
            <span className="status-pill">Coach AI</span>
            <span className="status-pill">спортивный менеджер</span>
          </div>

          <h1 className="mx-auto max-w-3xl text-[2.15rem] font-semibold leading-[0.98] sm:text-5xl lg:mx-0 xl:text-7xl">
            Личный спортивный менеджер
          </h1>

          <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-muted-foreground sm:mt-4 sm:text-lg sm:leading-7 lg:mx-0">
            Coach AI превращает цель в понятную систему: тренировки, питание,
            нагрузка, восстановление и прогресс в одном маршруте.
          </p>

          <Button size="lg" asChild className="neon-action mx-auto mt-5 w-full max-w-xs sm:mt-7 lg:mx-0">
            <Link href="/register">
              <span className="relative z-10 flex items-center gap-2">
                Собрать личный план
                <ArrowRight className="size-4" />
              </span>
            </Link>
          </Button>
        </div>

        <div className="cockpit-panel panel-reveal relative min-h-0 overflow-hidden rounded-lg p-3 sm:p-4">
          <div className="flex h-full min-h-0 flex-col">
            <div className="flex shrink-0 items-start justify-between gap-4 border-b border-[#712031]/55 pb-3">
              <div className="min-w-0">
                <p className="tactical-readout text-[0.58rem] text-muted-foreground sm:text-[0.66rem]">
                  продуктовая система
                </p>
                <h2 className="mt-1 text-lg font-semibold leading-tight sm:text-2xl">
                  Что Coach AI берет на себя
                </h2>
              </div>
              <div className="hidden items-center gap-2 sm:flex">
                {[ShieldCheck, Target].map((Icon, index) => (
                  <div
                    key={index}
                    className="glass-lane interactive-lane flex size-10 items-center justify-center rounded-lg"
                  >
                    <Icon className="size-4 text-primary" />
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-3 grid min-h-0 flex-1 grid-cols-2 gap-2 sm:gap-3">
              {productCards.map((card) => (
                <div
                  key={card.title}
                  className="glass-lane interactive-lane flex min-h-0 flex-col rounded-lg p-3 sm:p-4"
                >
                  <div className="mb-2 flex items-center justify-between gap-2">
                    <card.icon className="size-4 shrink-0 text-primary sm:size-5" />
                    <span className="h-px flex-1 bg-[#712031]/55" />
                  </div>
                  <h3 className="text-sm font-semibold leading-tight sm:text-base">
                    {card.title}
                  </h3>
                  <p className="mt-1 text-[0.72rem] leading-4 text-muted-foreground sm:mt-2 sm:text-sm sm:leading-5">
                    {card.text}
                  </p>
                </div>
              ))}
            </div>

            <div className="mt-3 hidden shrink-0 overflow-hidden rounded-lg border border-[#712031]/50 sm:block">
              {productFlow.map(([step, title, text]) => (
                <div
                  key={step}
                  className="grid grid-cols-[0.22fr_0.35fr_1fr] gap-3 border-b border-[#712031]/40 px-3 py-2 text-sm last:border-b-0"
                >
                  <span className="tactical-readout text-[0.64rem] text-primary">
                    {step}
                  </span>
                  <span className="font-semibold">{title}</span>
                  <span className="text-muted-foreground">{text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
