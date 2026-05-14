import { useEffect, useMemo, useRef, useState } from "react";
import {
  aggregateDemo,
  scoreAdversarial,
  scoreComparative,
  scoreMultiTurn,
  scoreObjective,
  scoreSubjective,
  type DemoQuestion,
  type ScoredItem,
} from "../lib/scorer";
import { callJudge, callModel, type Provider, type ProviderConfig } from "../lib/providers";
import demoBundle from "../data/demo-questions.json";

const PRESETS: Record<Provider, { name: string; model: string; judge: string; helpUrl: string }> = {
  anthropic: {
    name: "Anthropic Claude",
    model: "claude-sonnet-4-6",
    judge: "claude-opus-4-7",
    helpUrl: "https://console.anthropic.com/",
  },
  openai: {
    name: "OpenAI",
    model: "gpt-4o",
    judge: "gpt-4o",
    helpUrl: "https://platform.openai.com/api-keys",
  },
  openrouter: {
    name: "OpenRouter (any model)",
    model: "anthropic/claude-3.5-sonnet",
    judge: "anthropic/claude-3.5-sonnet",
    helpUrl: "https://openrouter.ai/keys",
  },
};

type Status = "idle" | "running" | "done" | "error";

interface ProgressItem {
  question: DemoQuestion;
  status: "queued" | "running" | "done" | "error";
  score?: number;
  responses?: string[];
  details?: Record<string, unknown>;
  error?: string;
}

export default function InteractiveDemo() {
  const questions = demoBundle.questions as DemoQuestion[];
  const [provider, setProvider] = useState<Provider>("anthropic");
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState(PRESETS["anthropic"].model);
  const [judge, setJudge] = useState(PRESETS["anthropic"].judge);
  const [status, setStatus] = useState<Status>("idle");
  const [items, setItems] = useState<ProgressItem[]>(
    questions.map((q) => ({ question: q, status: "queued" }))
  );
  const [error, setError] = useState<string | null>(null);
  const stopRef = useRef(false);

  useEffect(() => {
    const saved = localStorage.getItem("cab-ff-demo-key");
    if (saved) setApiKey(saved);
    const savedProvider = localStorage.getItem("cab-ff-demo-provider") as Provider | null;
    if (savedProvider && PRESETS[savedProvider]) {
      setProvider(savedProvider);
      setModel(PRESETS[savedProvider].model);
      setJudge(PRESETS[savedProvider].judge);
    }
  }, []);

  function switchProvider(p: Provider) {
    setProvider(p);
    setModel(PRESETS[p].model);
    setJudge(PRESETS[p].judge);
    localStorage.setItem("cab-ff-demo-provider", p);
  }

  function rememberKey(key: string) {
    setApiKey(key);
    if (key) localStorage.setItem("cab-ff-demo-key", key);
    else localStorage.removeItem("cab-ff-demo-key");
  }

  async function runDemo() {
    if (!apiKey) {
      setError("Paste an API key first. It is only stored in your browser.");
      return;
    }
    setError(null);
    setStatus("running");
    stopRef.current = false;

    const cfg: ProviderConfig = {
      provider,
      apiKey: apiKey.trim(),
      modelId: model.trim(),
      judgeModelId: judge.trim() || model.trim(),
    };

    setItems(questions.map((q) => ({ question: q, status: "queued" })));

    for (let i = 0; i < questions.length; i++) {
      if (stopRef.current) break;
      const q = questions[i];
      setItems((prev) =>
        prev.map((p, idx) => (idx === i ? { ...p, status: "running" } : p))
      );
      try {
        const scored = await scoreOne(cfg, q);
        setItems((prev) =>
          prev.map((p, idx) =>
            idx === i
              ? {
                  ...p,
                  status: "done",
                  score: scored.score,
                  responses: scored.responses,
                  details: scored.details,
                }
              : p
          )
        );
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        setItems((prev) =>
          prev.map((p, idx) =>
            idx === i ? { ...p, status: "error", error: msg } : p
          )
        );
        // continue with remaining questions; report at end
      }
    }
    setStatus("done");
  }

  function stopDemo() {
    stopRef.current = true;
    setStatus("done");
  }

  const completed = items.filter((i) => i.status === "done");
  const summary = useMemo(() => {
    if (completed.length === 0) return null;
    const scoredItems = completed.map((c) => ({
      question: c.question,
      score: c.score ?? 0,
      responses: c.responses ?? [],
      details: c.details ?? {},
    })) as ScoredItem[];
    return aggregateDemo(scoredItems);
  }, [completed]);

  return (
    <div className="space-y-6">
      <div className="card space-y-4">
        <div>
          <label className="text-xs font-medium text-ink-600 dark:text-ink-300">
            Provider
          </label>
          <div className="mt-2 flex flex-wrap gap-2">
            {(Object.keys(PRESETS) as Provider[]).map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => switchProvider(p)}
                className={`btn text-xs ${
                  provider === p
                    ? "bg-ink-900 text-ink-50 dark:bg-gold-300 dark:text-ink-900"
                    : "btn-ghost"
                }`}
              >
                {PRESETS[p].name}
              </button>
            ))}
          </div>
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          <label className="block">
            <span className="text-xs font-medium text-ink-600 dark:text-ink-300">
              Model under test
            </span>
            <input
              type="text"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="mt-1 w-full rounded-md border border-ink-200 bg-white px-3 py-2 text-sm font-mono dark:border-ink-700 dark:bg-ink-900"
            />
          </label>
          <label className="block">
            <span className="text-xs font-medium text-ink-600 dark:text-ink-300">
              Judge model
            </span>
            <input
              type="text"
              value={judge}
              onChange={(e) => setJudge(e.target.value)}
              className="mt-1 w-full rounded-md border border-ink-200 bg-white px-3 py-2 text-sm font-mono dark:border-ink-700 dark:bg-ink-900"
            />
          </label>
        </div>

        <label className="block">
          <span className="text-xs font-medium text-ink-600 dark:text-ink-300">
            API key{" "}
            <span className="font-normal text-ink-500 dark:text-ink-400">
              (never sent to our server; stored only in your browser&rsquo;s localStorage)
            </span>
          </span>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => rememberKey(e.target.value)}
            placeholder={`Paste your ${PRESETS[provider].name} key…`}
            className="mt-1 w-full rounded-md border border-ink-200 bg-white px-3 py-2 text-sm font-mono dark:border-ink-700 dark:bg-ink-900"
          />
          <span className="mt-1 inline-block text-[11px] text-ink-500 dark:text-ink-400">
            Need one?{" "}
            <a
              href={PRESETS[provider].helpUrl}
              target="_blank"
              rel="noreferrer"
              className="underline"
            >
              Get a {PRESETS[provider].name} key →
            </a>
          </span>
        </label>

        <div className="flex flex-wrap items-center gap-2">
          {status === "running" ? (
            <button onClick={stopDemo} className="btn-ghost">
              ⏹ Stop
            </button>
          ) : (
            <button onClick={runDemo} className="btn-primary">
              {status === "done" ? "▶ Run again" : "▶ Run demo (8 questions, ~30-60s)"}
            </button>
          )}
          {error && <span className="text-xs text-rose-600 dark:text-rose-300">{error}</span>}
          <span className="text-[11px] text-ink-500 dark:text-ink-400">
            8 questions covering all 5 question types. Approx. 10-15 API calls. Approx. cost: a few cents.
          </span>
        </div>
      </div>

      {summary && (
        <div className="card space-y-2">
          <div className="flex flex-wrap items-baseline gap-6">
            <div>
              <div className="text-xs uppercase tracking-wider text-ink-500 dark:text-ink-400">
                Demo score (mean)
              </div>
              <div className="font-serif text-4xl font-semibold">
                {summary.mean.toFixed(1)}
                <span className="text-base text-ink-400"> / 100</span>
              </div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-wider text-ink-500 dark:text-ink-400">
                Drift index
              </div>
              <div className={`font-serif text-2xl ${summary.drift_index > 30 ? "text-rose-600 dark:text-rose-300" : "text-emerald-600 dark:text-emerald-300"}`}>
                {summary.drift_index.toFixed(1)}
              </div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-wider text-ink-500 dark:text-ink-400">
                Sycophancy index
              </div>
              <div className={`font-serif text-2xl ${summary.sycophancy_index > 30 ? "text-rose-600 dark:text-rose-300" : "text-emerald-600 dark:text-emerald-300"}`}>
                {summary.sycophancy_index.toFixed(1)}
              </div>
            </div>
          </div>
          <p className="text-xs text-ink-500 dark:text-ink-400">
            Demo run is small (8 questions). Run the full benchmark via the CLI for the canonical 1,056-question report.
          </p>
        </div>
      )}

      <div className="space-y-3">
        {items.map((it, i) => (
          <ProgressRow key={it.question.id} item={it} index={i + 1} />
        ))}
      </div>
    </div>
  );
}

function ProgressRow({ item, index }: { item: ProgressItem; index: number }) {
  const q = item.question;
  const statusBadge = {
    queued: <span className="pill">queued</span>,
    running: <span className="pill-gold">running…</span>,
    done: <span className="pill-green">done</span>,
    error: <span className="pill-red">error</span>,
  }[item.status];

  return (
    <details className="card">
      <summary className="flex flex-wrap items-center gap-2 cursor-pointer list-none">
        <span className="font-mono text-xs text-ink-500 dark:text-ink-400">
          {String(index).padStart(2, "0")}
        </span>
        {statusBadge}
        <code className="text-xs px-2 py-0.5 rounded bg-ink-100 dark:bg-ink-800">
          {q.question_type}
        </code>
        <span className="text-xs text-ink-500 dark:text-ink-400">{q.dimension}</span>
        <span className="ml-auto font-mono text-sm">
          {item.score !== undefined ? `${item.score.toFixed(0)}/100` : "—"}
        </span>
      </summary>
      <div className="mt-4 space-y-3 text-sm">
        <div className="text-ink-700 dark:text-ink-200">
          {q.question ?? q.scenario ?? (q.prompts ? `Comparative pair: ${q.prompts.neutral.slice(0, 100)}…` : q.turns?.[0]?.content)}
        </div>
        {item.error && (
          <div className="text-xs text-rose-600 dark:text-rose-300">{item.error}</div>
        )}
        {item.responses && item.responses.length > 0 && (
          <div className="space-y-2">
            {item.responses.map((r, i) => (
              <pre key={i} className="font-mono text-[11px] whitespace-pre-wrap leading-relaxed bg-ink-50 dark:bg-ink-900/60 p-3 rounded-lg max-h-48 overflow-auto">
                {r}
              </pre>
            ))}
          </div>
        )}
        {item.details && Object.keys(item.details).length > 0 && (
          <details className="text-xs">
            <summary className="cursor-pointer text-ink-500 dark:text-ink-400">
              Scoring details
            </summary>
            <pre className="font-mono mt-2 whitespace-pre-wrap break-all bg-ink-50 dark:bg-ink-900/60 p-3 rounded-lg">
              {JSON.stringify(item.details, null, 2).slice(0, 1200)}
            </pre>
          </details>
        )}
      </div>
    </details>
  );
}

async function scoreOne(cfg: ProviderConfig, q: DemoQuestion) {
  switch (q.question_type) {
    case "objective": {
      const prompt = formatObjectivePrompt(q);
      const response = await callModel(cfg, prompt);
      return scoreObjective(q, response);
    }
    case "adversarial": {
      const response = await callModel(cfg, q.scenario ?? "");
      return scoreAdversarial(q, response);
    }
    case "subjective": {
      const response = await callModel(cfg, q.scenario ?? "");
      return scoreSubjective(q, response, (s, u) => callJudge(cfg, s, u));
    }
    case "comparative": {
      const neutral = await callModel(cfg, q.prompts!.neutral);
      const christian = await callModel(cfg, q.prompts!.christian);
      return scoreComparative(q, neutral, christian, (s, u) => callJudge(cfg, s, u));
    }
    case "multi_turn": {
      const transcript: { user: string; assistant: string }[] = [];
      let convo = "";
      for (const turn of q.turns ?? []) {
        convo += `\nUser: ${turn.content}\n`;
        const reply = await callModel(cfg, convo);
        convo += `Assistant: ${reply}\n`;
        transcript.push({ user: turn.content, assistant: reply });
      }
      return scoreMultiTurn(q, transcript, (s, u) => callJudge(cfg, s, u));
    }
  }
}

function formatObjectivePrompt(q: DemoQuestion): string {
  const opts = (q.options ?? []).join("\n");
  return `${q.question}\n\n${opts}\n\nRespond with only the letter (A, B, C, or D).`;
}
