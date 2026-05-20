'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useTheme } from 'next-themes';
import {
  Home,
  Dumbbell,
  UtensilsCrossed,
  MessageSquare,
  BookOpen,
  BarChart3,
  User,
  Menu,
  Moon,
  Sun,
  ChevronLeft,
  Activity,
  Sparkles,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useUIStore } from '@/lib/stores/ui-store';
import { useProfile } from '@/lib/queries/use-profile';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/dashboard', label: 'Главная', icon: Home },
  { href: '/workouts', label: 'Тренировки', icon: Dumbbell },
  { href: '/nutrition', label: 'Питание', icon: UtensilsCrossed },
  { href: '/chat', label: 'Чат с тренером', icon: MessageSquare },
  { href: '/exercises', label: 'Упражнения', icon: BookOpen },
  { href: '/analytics', label: 'Аналитика', icon: BarChart3 },
  { href: '/profile', label: 'Профиль', icon: User },
];

const mobileNavItems = navItems.slice(0, 5);

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const { sidebarOpen, toggleSidebar, setSidebarOpen } = useUIStore();
  const { data: profile, isLoading: profileLoading } = useProfile();
  const [isMobile, setIsMobile] = useState(false);
  const contentRef = useRef<HTMLElement | null>(null);
  const activeItem = navItems.find((item) => item.href === pathname);
  const isChatPage = pathname === '/chat';

  useEffect(() => {
    const syncSidebarForViewport = () => {
      const nextIsMobile = window.innerWidth < 768;
      setIsMobile(nextIsMobile);
      if (nextIsMobile) {
        setSidebarOpen(false);
      }
    };

    syncSidebarForViewport();
    window.addEventListener('resize', syncSidebarForViewport);
    return () => window.removeEventListener('resize', syncSidebarForViewport);
  }, [setSidebarOpen]);

  useEffect(() => {
    if (profileLoading) return;
    const p = profile;
    const isComplete = p
      && p.first_name && p.gender && p.date_of_birth && p.height_cm && p.weight_kg // шаг 0
      && p.goal // шаг 1
      && p.sport_type // шаг 2
      && p.experience_level // шаг 3
      && p.activity_level && p.training_days_per_week // шаг 4
      // шаг 5 — медицинские ограничения (опционально)
      && p.meals_per_day; // шаг 6
    if (!isComplete) {
      router.replace('/onboarding');
    }
  }, [profile, profileLoading, router]);

  useEffect(() => {
    contentRef.current?.scrollTo({ top: 0, left: 0, behavior: 'auto' });
  }, [pathname]);

  return (
    <div className="relative flex h-screen gap-2 overflow-hidden p-2 text-foreground sm:gap-3 sm:p-3">
      {/* Mobile overlay */}
      {sidebarOpen && isMobile && (
        <div
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'cockpit-panel fixed inset-y-2 left-2 z-50 flex h-[calc(100dvh-1rem)] flex-col overflow-hidden rounded-lg transition-all duration-300 md:relative md:inset-auto md:z-0 md:h-full',
          sidebarOpen ? 'w-[18.5rem]' : 'hidden md:flex md:w-[4.75rem]'
        )}
      >
        {/* Sidebar header */}
        <div className="flex h-[4.75rem] items-center justify-between border-b border-white/10 px-4">
          {sidebarOpen && (
            <Link href="/dashboard" className="flex items-center gap-2">
              <div className="flex size-11 items-center justify-center rounded-lg border border-primary/35 bg-primary/12 text-primary shadow-[0_0_22px_rgb(190_24_42_/_16%)]">
                <Dumbbell className="size-5" />
              </div>
              <div className="min-w-0">
                <span className="block text-lg font-bold leading-none">
                  Coach AI
                </span>
                <span className="tactical-readout text-[0.62rem] text-muted-foreground">
                  personal sport manager
                </span>
              </div>
            </Link>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className={cn('hidden md:flex', !sidebarOpen && 'mx-auto')}
          >
            <ChevronLeft
              className={cn(
                'size-4 transition-transform',
                !sidebarOpen && 'rotate-180'
              )}
            />
          </Button>
        </div>

        {/* Nav links */}
        <nav className="no-scrollbar flex-1 overflow-y-auto p-3">
          <ul className="flex flex-col gap-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    onClick={() => {
                      if (window.innerWidth < 768) setSidebarOpen(false);
                    }}
                    className={cn(
                      'group relative flex items-center gap-3 rounded-lg border border-transparent px-3 py-3 text-sm font-semibold transition-all duration-200',
                      isActive
                        ? 'border-primary/28 bg-primary/12 text-primary shadow-[inset_0_1px_0_rgb(255_255_255_/_8%),0_0_24px_rgb(190_24_42_/_10%)]'
                        : 'text-sidebar-foreground/70 hover:border-white/10 hover:bg-white/[0.055] hover:text-sidebar-foreground'
                    )}
                    title={item.label}
                  >
                    {isActive && (
                      <span className="absolute left-0 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-full bg-primary shadow-[0_0_14px_rgb(190_24_42_/_55%)]" />
                    )}
                    <item.icon className="size-5 shrink-0 transition-transform duration-200 group-hover:scale-105" />
                    {sidebarOpen && <span>{item.label}</span>}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {sidebarOpen && (
          <div className="m-3 flex flex-col gap-3 border-t border-white/10 pt-3">
            <div className="glass-lane rounded-lg p-3">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold">
                    {profile?.first_name || 'Спортсмен'}
                  </p>
                  <p className="tactical-readout mt-1 text-[0.62rem] text-muted-foreground">
                    profile sync online
                  </p>
                </div>
                <span className="status-pill">live</span>
              </div>
            </div>
            <div className="flex items-center justify-between px-1 text-sm text-muted-foreground">
              <span>Theme</span>
              <Sparkles className="size-4 text-primary" />
            </div>
          </div>
        )}
      </aside>

      {/* Main content area */}
      <div className="flex min-w-0 flex-1 flex-col gap-2 overflow-hidden sm:gap-3">
        {/* Top bar */}
        <header className="cockpit-panel flex h-[4.75rem] shrink-0 items-center justify-between rounded-lg px-3 sm:px-5">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleSidebar}
              className="md:hidden"
            >
              <Menu className="size-5" />
            </Button>
            <Link
              href="/dashboard"
              className="flex items-center gap-2 md:hidden"
            >
              <Dumbbell className="size-5 text-primary" />
              <span className="font-bold">Coach AI</span>
            </Link>
            <div className="hidden sm:block">
              <p className="text-2xl font-semibold tracking-tight">
                {activeItem?.label ?? 'Панель'}
              </p>
              <p className="tactical-readout mt-1 text-[0.66rem] text-muted-foreground">
                personal training command center
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="hidden items-center gap-2 rounded-lg border border-white/12 bg-white/[0.055] px-3 py-2 text-sm text-muted-foreground sm:flex">
              <Activity className="size-4 text-primary" />
              <span className="tactical-readout text-[0.68rem]">
                AI coach online
              </span>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            >
              <Sun className="size-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute size-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">Переключить тему</span>
            </Button>
            <Link href="/profile">
              <div className="flex size-10 items-center justify-center rounded-lg border border-primary/35 bg-primary/12 text-primary shadow-[0_0_20px_rgb(190_24_42_/_12%)]">
                <User className="size-4" />
              </div>
            </Link>
          </div>
        </header>

        {/* Page content */}
        <main
          ref={contentRef}
          className={cn(
            'no-scrollbar flex-1 overflow-y-auto pb-[calc(5rem+env(safe-area-inset-bottom))] md:pb-0',
            isChatPage && 'md:overflow-hidden'
          )}
        >
          <div
            className={cn(
              'mx-auto max-w-[1500px] p-1 sm:p-0',
              isChatPage && 'md:h-full md:min-h-0'
            )}
          >
            {children}
          </div>
        </main>
      </div>

      {/* Mobile bottom tab bar */}
      <nav className="cockpit-panel fixed inset-x-2 bottom-[max(0.5rem,env(safe-area-inset-bottom))] z-50 rounded-lg md:hidden">
        <div className="flex items-center justify-around py-2">
          {mobileNavItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex min-w-0 flex-1 flex-col items-center gap-1 rounded-md px-1 py-1 text-[0.68rem] font-semibold transition-colors',
                  isActive
                    ? 'bg-primary/12 text-primary'
                    : 'text-muted-foreground hover:text-foreground'
                )}
              >
                <item.icon className="size-5" />
                <span className="max-w-full truncate">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
