# CAB-FF — Website

The marketing site, interactive demo, and leaderboard for CAB-FF.
Built with [Astro](https://astro.build) + Tailwind + a single React island
for the in-browser demo. Deploys to GitHub Pages automatically on every
push to `main` (see `.github/workflows/deploy-web.yml`).

## Pages

| Route | Purpose |
|---|---|
| `/` | Landing — hero, failure modes, audiences, benchmark overview, Gloo comparison, leaderboard preview, CTA |
| `/try` | **Interactive demo.** Visitor pastes API key, picks a model, watches CAB-FF score it on 8 representative questions in-browser |
| `/methodology` | Pipeline diagram, scoring formula, dimensions, axes, question types, judge panel |
| `/compare` | Full side-by-side vs Gloo FAI-C, including the failure-mode → probe map |
| `/leaderboard` | Auto-generated from `results/baselines/*.json` in the repo |

## Develop

```bash
cd web
npm install
npm run dev       # http://localhost:4321/SoliDeoGloria
```

## Build

```bash
npm run build
npm run preview
```

The build first runs `scripts/bundle-demo-questions.mjs` which extracts
8 curated demo questions from `../data/CAB_FF_v3_dataset.json` into
`src/data/demo-questions.json` so the React island has them bundled
client-side.

## Privacy and cost

The interactive demo at `/try` runs **entirely in the visitor's browser**.
We do not have a server. The visitor's API key never leaves their browser
— calls go directly to the provider (Anthropic, OpenAI, OpenRouter). All
API costs are borne by the visitor on their own account.

## Theme

- Type: Inter (sans), Lora (serif), JetBrains Mono (code) via Google Fonts
- Light/dark mode toggle (persisted in localStorage)
- Accent: warm gold (`gold-300` etc. — see `tailwind.config.mjs`)
- Layout: max-width 6xl section containers, sticky header

## How the leaderboard data flow works

`src/lib/leaderboard.ts` reads `../results/baselines/*.json` at build
time (Astro is static, so this happens once per build). New baseline
runs added to that directory get picked up on the next deploy. The CI
workflow at `.github/workflows/deploy-web.yml` is path-triggered on
`results/baselines/**` so updates to baseline data alone (no other
changes) still redeploy the site.
