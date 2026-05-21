import type { MetadataRoute } from "next";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://coach-ai.ru";

const PRIVATE_PATHS = [
  "/api/",
  "/dashboard",
  "/dashboard/",
  "/workouts",
  "/workouts/",
  "/nutrition",
  "/nutrition/",
  "/chat",
  "/chat/",
  "/exercises",
  "/exercises/",
  "/analytics",
  "/analytics/",
  "/profile",
  "/profile/",
  "/onboarding",
  "/onboarding/",
  "/verify-email",
  "/uploads/",
  "/_next/",
];

const AI_BOTS = [
  "GPTBot",
  "OAI-SearchBot",
  "ChatGPT-User",
  "ClaudeBot",
  "Claude-Web",
  "anthropic-ai",
  "PerplexityBot",
  "Perplexity-User",
  "Google-Extended",
  "Applebot-Extended",
  "YandexGPT",
  "Bytespider",
  "Amazonbot",
  "Meta-ExternalAgent",
  "Meta-ExternalFetcher",
  "DuckAssistBot",
  "MistralAI-User",
  "cohere-ai",
];

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: PRIVATE_PATHS,
      },
      ...AI_BOTS.map((userAgent) => ({
        userAgent,
        allow: "/",
        disallow: PRIVATE_PATHS,
      })),
    ],
    sitemap: `${SITE_URL}/sitemap.xml`,
    host: SITE_URL,
  };
}
