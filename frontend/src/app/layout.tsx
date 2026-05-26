import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { QueryProvider } from "@/lib/providers/query-provider";
import { ThemeProvider } from "@/lib/providers/theme-provider";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const matrixBursts = Array.from({ length: 12 }, (_, index) => index + 1);

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://coach-ai.ru";
const SITE_NAME = "Coach AI";
const SITE_DESCRIPTION =
  "Адаптивная платформа для спортивного планирования с ИИ: персональные планы тренировок и питания, дневник прогресса, распознавание еды по фото и чат с ИИ-тренером.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "Coach AI — личный спортивный менеджер с ИИ",
    template: "%s · Coach AI",
  },
  description: SITE_DESCRIPTION,
  applicationName: SITE_NAME,
  keywords: [
    "ИИ тренер",
    "AI тренер",
    "план тренировок",
    "персональный план тренировок",
    "питание для спортсменов",
    "приложение для тренировок",
    "адаптивные тренировки",
    "спортивный менеджер",
    "Coach AI",
  ],
  authors: [{ name: SITE_NAME }],
  creator: SITE_NAME,
  publisher: SITE_NAME,
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    locale: "ru_RU",
    url: SITE_URL,
    siteName: SITE_NAME,
    title: "Coach AI — личный спортивный менеджер с ИИ",
    description: SITE_DESCRIPTION,
  },
  twitter: {
    card: "summary_large_image",
    title: "Coach AI — личный спортивный менеджер с ИИ",
    description: SITE_DESCRIPTION,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-snippet": -1,
      "max-image-preview": "large",
      "max-video-preview": -1,
    },
  },
  formatDetection: {
    telephone: false,
    email: false,
    address: false,
  },
};

const organizationSchema = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: SITE_NAME,
  url: SITE_URL,
  logo: `${SITE_URL}/favicon.ico`,
  description: SITE_DESCRIPTION,
};

const softwareSchema = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: SITE_NAME,
  applicationCategory: "HealthApplication",
  operatingSystem: "Web",
  inLanguage: "ru",
  url: SITE_URL,
  description: SITE_DESCRIPTION,
  offers: {
    "@type": "Offer",
    price: "0",
    priceCurrency: "RUB",
  },
};

const websiteSchema = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: SITE_NAME,
  url: SITE_URL,
  inLanguage: "ru",
};

const jsonLdSchemas = [organizationSchema, softwareSchema, websiteSchema];

function serializeJsonLd(schema: Record<string, unknown>): string {
  return JSON.stringify(schema).replace(/</g, "\\u003c");
}

const PALETTE_BOOTSTRAP_SCRIPT = `(function(){try{var allowed=['crimson','aurora','violet','cyan','emerald','amber'];var s=localStorage.getItem('coach-palette');var p='crimson';if(s){var o=JSON.parse(s);if(o&&o.state&&allowed.indexOf(o.state.palette)!==-1)p=o.state.palette;}document.documentElement.classList.add('theme-'+p);}catch(e){document.documentElement.classList.add('theme-crimson');}})();`;

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: PALETTE_BOOTSTRAP_SCRIPT }} />
        {jsonLdSchemas.map((schema, index) => (
          <script
            key={index}
            type="application/ld+json"
            dangerouslySetInnerHTML={{ __html: serializeJsonLd(schema) }}
          />
        ))}
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <div aria-hidden="true" className="global-matrix-field">
          {matrixBursts.map((burst) => (
            <span
              key={burst}
              className={`matrix-burst matrix-burst-${burst}`}
            />
          ))}
        </div>
        <div className="app-shell">
          <ThemeProvider>
            <QueryProvider>
              {children}
              <Toaster />
            </QueryProvider>
          </ThemeProvider>
        </div>
      </body>
    </html>
  );
}
