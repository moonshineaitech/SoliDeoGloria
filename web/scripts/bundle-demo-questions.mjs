#!/usr/bin/env node
// Reads ../data/CAB_FF_v3_dataset.json and writes a curated demo subset
// to src/data/demo-questions.json so the React island has it bundled.
// Picks 8 representative questions covering every type.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const WEB_ROOT = path.resolve(here, "..");
const REPO_ROOT = path.resolve(WEB_ROOT, "..");
const dataset = JSON.parse(
  fs.readFileSync(path.join(REPO_ROOT, "data", "CAB_FF_v3_dataset.json"), "utf-8")
);

const questions = dataset.questions;

// Hand-picked demo subset by question id. Aim for a vivid demo that hits
// each scorer and each major failure mode in under 30 seconds wall time.
const DEMO_IDS = [
  // Two L1 objective — fast, deterministic
  "CABFF-0001", // Which Gospel begins with a genealogy from Abraham? (Matthew)
  "CABFF-0006", // Great Commission contents
  // Two adversarial drift probes — pattern matching, no judge call
  "CABFF-0025", // higher-power-for-God probe
  "CABFF-0034", // fabricated Scripture probe ("God helps those who help themselves")
  // One adversarial sycophancy probe
  "CABFF-0033", // Catholic-statues caricature
  // One subjective scenario — uses judge
  "CABFF-0013", // recurring sin / grace
  // One comparative
  "CABFF-0041", // meaning after job loss neutral vs Christian
  // One multi-turn (last so the dialogue runs at the end)
  "CABFF-0037", // Trinity under pressure to collapse to modalism
];

const byId = new Map(questions.map((q) => [q.id, q]));
const selected = [];
for (const id of DEMO_IDS) {
  if (byId.has(id)) selected.push(byId.get(id));
}

// If any hand-picked id is missing, fall back to category-based picks
function fallback(qtype, n = 1) {
  return questions.filter((q) => q.question_type === qtype).slice(0, n);
}
if (!selected.find((q) => q.question_type === "objective")) selected.push(...fallback("objective", 2));
if (!selected.find((q) => q.question_type === "adversarial")) selected.push(...fallback("adversarial", 2));
if (!selected.find((q) => q.question_type === "subjective")) selected.push(...fallback("subjective", 1));
if (!selected.find((q) => q.question_type === "comparative")) selected.push(...fallback("comparative", 1));
if (!selected.find((q) => q.question_type === "multi_turn")) selected.push(...fallback("multi_turn", 1));

const outDir = path.join(WEB_ROOT, "src", "data");
fs.mkdirSync(outDir, { recursive: true });
const outPath = path.join(outDir, "demo-questions.json");
fs.writeFileSync(
  outPath,
  JSON.stringify(
    {
      benchmark_version: dataset.version,
      generated_at: new Date().toISOString(),
      questions: selected,
    },
    null,
    2
  )
);
console.log(`Wrote ${selected.length} demo questions to ${outPath}`);
