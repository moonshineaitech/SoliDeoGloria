export const SITE = {
  name: "CAB-FF",
  longName: "CAB-FF — The Christian AI Benchmark",
  tagline:
    "The open Christian AI benchmark. 1,056 questions, 8 dimensions, 9 tradition-aware judges.",
  repo: "https://github.com/moonshineaitech/SoliDeoGloria",
  issues: "https://github.com/moonshineaitech/SoliDeoGloria/issues",
  publisher: "Eldest AI LLC dba GoldRock AI",
  publisherSite: "https://SoliDeoGloria.ai",
  email: "research@solideogloria.ai",
  version: "3.0.1",
  questionCount: 1056,
  testCount: 47,
} as const;

export const NAV = [
  { href: "/", label: "Home" },
  { href: "/try", label: "Try it" },
  { href: "/methodology", label: "Methodology" },
  { href: "/compare", label: "vs Gloo" },
  { href: "/leaderboard", label: "Leaderboard" },
] as const;
