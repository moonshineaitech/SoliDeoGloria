// Browser-side LLM provider callers. The user's API key never leaves
// the browser — calls go directly to the provider's CORS-friendly endpoint.

export type Provider = "anthropic" | "openai" | "openrouter";

export interface ProviderConfig {
  provider: Provider;
  apiKey: string;
  modelId: string;
  judgeModelId: string;
}

export async function callModel(
  cfg: ProviderConfig,
  prompt: string,
  opts?: { system?: string; temperature?: number; maxTokens?: number }
): Promise<string> {
  const temperature = opts?.temperature ?? 0;
  const maxTokens = opts?.maxTokens ?? 1024;
  switch (cfg.provider) {
    case "anthropic":
      return callAnthropic(cfg.apiKey, cfg.modelId, prompt, {
        system: opts?.system,
        temperature,
        maxTokens,
      });
    case "openai":
      return callOpenAI(cfg.apiKey, cfg.modelId, prompt, {
        system: opts?.system,
        temperature,
        maxTokens,
      });
    case "openrouter":
      return callOpenRouter(cfg.apiKey, cfg.modelId, prompt, {
        system: opts?.system,
        temperature,
        maxTokens,
      });
  }
}

export async function callJudge(
  cfg: ProviderConfig,
  system: string,
  user: string,
  opts?: { temperature?: number; maxTokens?: number }
): Promise<string> {
  const temperature = opts?.temperature ?? 0.2;
  const maxTokens = opts?.maxTokens ?? 1024;
  switch (cfg.provider) {
    case "anthropic":
      return callAnthropic(cfg.apiKey, cfg.judgeModelId, user, {
        system,
        temperature,
        maxTokens,
      });
    case "openai":
      return callOpenAI(cfg.apiKey, cfg.judgeModelId, user, {
        system,
        temperature,
        maxTokens,
      });
    case "openrouter":
      return callOpenRouter(cfg.apiKey, cfg.judgeModelId, user, {
        system,
        temperature,
        maxTokens,
      });
  }
}

interface CallOpts {
  system?: string;
  temperature: number;
  maxTokens: number;
}

async function callAnthropic(
  apiKey: string,
  model: string,
  prompt: string,
  opts: CallOpts
): Promise<string> {
  const body: Record<string, unknown> = {
    model,
    max_tokens: opts.maxTokens,
    temperature: opts.temperature,
    messages: [{ role: "user", content: prompt }],
  };
  if (opts.system) body.system = opts.system;
  const resp = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
      "anthropic-dangerous-direct-browser-access": "true",
      "content-type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`Anthropic ${resp.status}: ${text.slice(0, 200)}`);
  }
  const data = await resp.json();
  return (data.content ?? [])
    .map((b: { type: string; text?: string }) => b.text ?? "")
    .join("");
}

async function callOpenAI(
  apiKey: string,
  model: string,
  prompt: string,
  opts: CallOpts
): Promise<string> {
  const messages: Array<{ role: string; content: string }> = [];
  if (opts.system) messages.push({ role: "system", content: opts.system });
  messages.push({ role: "user", content: prompt });
  const resp = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model,
      messages,
      max_tokens: opts.maxTokens,
      temperature: opts.temperature,
    }),
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`OpenAI ${resp.status}: ${text.slice(0, 200)}`);
  }
  const data = await resp.json();
  return data.choices?.[0]?.message?.content ?? "";
}

async function callOpenRouter(
  apiKey: string,
  model: string,
  prompt: string,
  opts: CallOpts
): Promise<string> {
  const messages: Array<{ role: string; content: string }> = [];
  if (opts.system) messages.push({ role: "system", content: opts.system });
  messages.push({ role: "user", content: prompt });
  const resp = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "content-type": "application/json",
      "HTTP-Referer": "https://github.com/moonshineaitech/SoliDeoGloria",
      "X-Title": "CAB-FF live demo",
    },
    body: JSON.stringify({
      model,
      messages,
      max_tokens: opts.maxTokens,
      temperature: opts.temperature,
    }),
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`OpenRouter ${resp.status}: ${text.slice(0, 200)}`);
  }
  const data = await resp.json();
  return data.choices?.[0]?.message?.content ?? "";
}
