import Link from "next/link";
import { Button } from "@/components/ui/button";
import { MessageSquare, Dumbbell, UtensilsCrossed } from "lucide-react";

const features = [
  {
    icon: MessageSquare,
    title: "ИИ-тренер",
    description:
      "Персональный тренер на базе ИИ, который ответит на любые вопросы о тренировках, технике и восстановлении.",
  },
  {
    icon: Dumbbell,
    title: "Программа тренировок",
    description:
      "Индивидуальная программа тренировок, адаптированная под ваши цели, уровень подготовки и доступное оборудование.",
  },
  {
    icon: UtensilsCrossed,
    title: "План питания",
    description:
      "Сбалансированный рацион с учётом ваших целей, предпочтений и особенностей организма.",
  },
];

export default function LandingPage() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-primary/10" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-transparent to-transparent" />
        <div className="relative mx-auto max-w-7xl px-4 py-24 sm:px-6 sm:py-32 lg:px-8 lg:py-40">
          <div className="mx-auto max-w-3xl text-center">
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
              <span className="bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                Твой{" "}
              </span>
              <span className="bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                ИИ-тренер
              </span>
            </h1>
            <p className="mt-6 text-lg leading-8 text-muted-foreground sm:text-xl">
              Персонализированные тренировки, питание и восстановление с помощью
              искусственного интеллекта
            </p>
            <div className="mt-10 flex items-center justify-center gap-4">
              <Button size="lg" asChild className="text-base px-8 h-12">
                <Link href="/register">Начать бесплатно</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="mx-auto w-full max-w-7xl px-4 pb-24 sm:px-6 lg:px-8">
        <div className="grid w-full grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="group w-full rounded-xl border border-border/50 bg-gradient-to-b from-card to-card/50 p-6 transition-all duration-300 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5"
            >
              <div className="mb-4 flex size-12 items-center justify-center rounded-lg bg-primary/10 text-primary transition-colors group-hover:bg-primary/20">
                <feature.icon className="size-6" />
              </div>
              <h3 className="text-lg font-semibold">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
