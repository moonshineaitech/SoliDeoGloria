// Reads `results/baselines/*.json` at build time and exposes a sorted list.
// Falls back to a small "be the first" placeholder list if none exist yet.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export interface BaselineRun {
  model: string;
  judge?: string;
  provider?: string;
  cab_ff_score: number;
  flourishing_score: number;
  faithfulness_index: number;
  drift_index: number;
  sycophancy_index: number;
  questions: number;
  ts: string;
  link?: string;
}

function discoverBaselineDir(): string {
  const here = path.dirname(fileURLToPath(import.meta.url));
  // web/src/lib/leaderboard.ts → up three levels → repo root → results/baselines
  return path.resolve(here, "..", "..", "..", "results", "baselines");
}

export function loadBaselines(): BaselineRun[] {
  const dir = discoverBaselineDir();
  if (!fs.existsSync(dir)) return [];
  const runs: BaselineRun[] = [];
  for (const entry of fs.readdirSync(dir)) {
    if (!entry.endsWith(".json")) continue;
    const full = path.join(dir, entry);
    try {
      const raw = JSON.parse(fs.readFileSync(full, "utf-8"));
      const summary = raw.summary ?? raw;
      const meta = raw.metadata ?? {};
      runs.push({
        model: raw.model ?? entry.replace(/\.json$/, ""),
        judge: raw.judge ?? meta.judge,
        provider: raw.provider ?? meta.provider,
        cab_ff_score: summary.cab_ff_score ?? 0,
        flourishing_score: summary.flourishing_score ?? 0,
        faithfulness_index: summary.faithfulness_index ?? 0,
        drift_index: summary.drift_index ?? 0,
        sycophancy_index: summary.sycophancy_index ?? 0,
        questions: summary.total_questions ?? meta.questions_evaluated ?? 0,
        ts: meta.timestamp ?? raw.ts ?? "",
        link: raw.link ?? `https://github.com/moonshineaitech/SoliDeoGloria/blob/main/results/baselines/${entry}`,
      });
    } catch {
      // skip malformed files
    }
  }
  runs.sort((a, b) => b.cab_ff_score - a.cab_ff_score);
  return runs;
}
