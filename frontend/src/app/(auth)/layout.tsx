import { AuthViewportLock } from '@/components/auth/auth-viewport-lock';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="fixed inset-0 overflow-hidden bg-background">
      <AuthViewportLock />
      <main className="relative h-dvh overflow-hidden px-3 py-3 sm:px-6 sm:py-6">
        <div className="mx-auto flex h-full max-w-6xl items-center justify-center">
          <div
            data-auth-form-scroll
            className="panel-reveal max-h-full w-full max-w-md overflow-y-auto overscroll-contain py-2 [-webkit-overflow-scrolling:touch]"
          >
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}
