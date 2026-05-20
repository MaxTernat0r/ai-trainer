export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <main className="flex min-h-dvh items-center justify-center px-3 py-6 sm:px-6 sm:py-10">
      <div className="panel-reveal w-full max-w-md">
        {children}
      </div>
    </main>
  );
}
