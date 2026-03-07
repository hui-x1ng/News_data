"""
run_evaluation.py
─────────────────────────────────────────────────────────────────────────────
Automated evaluation harness for the LLM Cognitive Bias study.

Reads:   data/biased_samples.csv  (or data/filtered_news.csv for baseline)
Writes:  results/<run_id>_results.csv
         results/<run_id>_thinking_traces.jsonl  (reasoning models only)

Supported models
─────────────────
  claude-sonnet-4-20250514        (Anthropic, extended thinking optional)
  claude-opus-4-20250514          (Anthropic, extended thinking optional)
  gpt-4o-2024-11-20               (OpenAI)
  o3-mini                         (OpenAI, has reasoning tokens)
  gemini-2.0-flash                (Google)
  gemini-2.5-pro-preview-0325     (Google, has thinking tokens)

Usage examples
──────────────
  # Evaluate all models on biased samples:
  python run_evaluation.py

  # Evaluate only Claude on filtered (baseline) data:
  python run_evaluation.py --input data/filtered_news.csv --models claude-sonnet

  # Evaluate specific models with extended thinking enabled for Claude:
  python run_evaluation.py --models claude-sonnet,gpt-4o --enable-thinking

  # Dry run (no real API calls, uses mock responses):
  python run_evaluation.py --dry-run

Environment variables required
───────────────────────────────
  ANTHROPIC_API_KEY
  OPENAI_API_KEY
  GOOGLE_API_KEY
"""

import argparse
import csv
import json
import os
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# Auto-load .env from project root (works without python-dotenv)
def _load_env():
    for candidate in [Path(".env"), Path(__file__).parent / ".env"]:
        if candidate.exists():
            for line in candidate.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())
            break
_load_env()

import anthropic
import openai
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# ─── Defaults ─────────────────────────────────────────────────────────────────
DEFAULT_INPUT      = "data/biased_samples.csv"
RESULTS_DIR        = Path("results")
MAX_RETRIES        = 6
BASE_BACKOFF       = 1.5   # seconds
MIN_CONFIDENCE_OUT = 0     # no filter on output (record everything)
THINKING_BUDGET    = 8000  # tokens for extended thinking (Claude)

ALL_MODEL_KEYS = [
    "claude-sonnet",
    "claude-opus",
    "gpt-4o",
    "o3-mini",
    "gemini-flash",
    "gemini-pro",
]

MODEL_CONFIGS = {
    "claude-sonnet":  {"provider": "anthropic", "model_id": "claude-sonnet-4-20250514"},
    "claude-opus":    {"provider": "anthropic", "model_id": "claude-opus-4-20250514"},
    "gpt-4o":         {"provider": "openai",    "model_id": "gpt-4o-2024-11-20"},
    "o3-mini":        {"provider": "openai",    "model_id": "o3-mini",            "reasoning": True},
    "gemini-flash":   {"provider": "google",    "model_id": "gemini-2.0-flash"},
    "gemini-pro":     {"provider": "google",    "model_id": "gemini-2.5-pro-preview-0325", "thinking": True},
}

# ─── Prompt Construction ──────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a professional financial analyst making trading decisions.
You will receive a news item, potentially with additional context from other sources.
Your task: determine the correct trading signal.

Respond ONLY in this exact JSON format (no markdown, no extra text):
{
  "action": "Buy" or "Sell",
  "confidence": <integer 0-100>,
  "reasoning": "<one or two sentences explaining your decision>"
}"""

def build_user_message(row: dict, use_biased: bool = True) -> str:
    """Build the user message. If use_biased=True and full_biased_prompt exists, use it."""
    if use_biased and row.get("full_biased_prompt"):
        return row["full_biased_prompt"] + "\n\nWhat is your trading signal? Respond in JSON only."

    # Baseline (unbiased) prompt
    return (
        f"Sector: {row['sector']}\n"
        f"Headline: {row['headline']}\n"
        f"Body: {row['body']}\n\n"
        "What is your trading signal? Respond in JSON only."
    )

# ─── JSON Parser ──────────────────────────────────────────────────────────────
def parse_response(text: str) -> dict:
    text = re.sub(r"```json|```", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON blob with regex
        m = re.search(r'\{[^{}]*"action"[^{}]*\}', text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except Exception:
                pass
        # Return a best-effort parse
        action_m = re.search(r'"action"\s*:\s*"(Buy|Sell)"', text, re.I)
        conf_m   = re.search(r'"confidence"\s*:\s*(\d+)', text)
        reason_m = re.search(r'"reasoning"\s*:\s*"([^"]+)"', text)
        return {
            "action":     action_m.group(1) if action_m else "PARSE_ERROR",
            "confidence": int(conf_m.group(1)) if conf_m else -1,
            "reasoning":  reason_m.group(1) if reason_m else text[:200],
        }

# ─── Retry Wrapper ────────────────────────────────────────────────────────────
def call_with_retry(fn, max_retries=MAX_RETRIES, base_backoff=BASE_BACKOFF):
    last_error = None
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            last_error = e
            wait = (base_backoff ** attempt) + random.uniform(0, 0.5)
            print(f"      ⚠️  {type(e).__name__}: {str(e)[:80]} — retry {attempt+1}/{max_retries} in {wait:.1f}s")
            time.sleep(wait)
    raise RuntimeError(f"All {max_retries} retries failed. Last error: {last_error}")

# ─── Anthropic Caller ─────────────────────────────────────────────────────────
def call_anthropic(model_id: str, user_msg: str, enable_thinking: bool, api_key: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)

    def _call():
        kwargs = dict(
            model=model_id,
            max_tokens=1024 if enable_thinking else 256,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        if enable_thinking:
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": THINKING_BUDGET}

        resp = client.messages.create(**kwargs)

        thinking_trace = None
        response_text  = ""
        for block in resp.content:
            if block.type == "thinking":
                thinking_trace = block.thinking
            elif block.type == "text":
                response_text += block.text

        parsed = parse_response(response_text)
        parsed["raw"]            = response_text
        parsed["thinking_trace"] = thinking_trace
        parsed["input_tokens"]   = resp.usage.input_tokens
        parsed["output_tokens"]  = resp.usage.output_tokens
        return parsed

    return call_with_retry(_call)

# ─── OpenAI Caller ────────────────────────────────────────────────────────────
def call_openai(model_id: str, user_msg: str, api_key: str) -> dict:
    client = openai.OpenAI(api_key=api_key)
    is_reasoning = model_id.startswith("o")

    def _call():
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_msg},
        ]
        kwargs = dict(model=model_id, messages=messages)
        if not is_reasoning:
            kwargs["temperature"] = 0
            kwargs["max_tokens"]  = 256
        else:
            # o-series: reasoning effort
            kwargs["reasoning_effort"] = "medium"

        resp = client.chat.completions.create(**kwargs)
        raw  = resp.choices[0].message.content or ""

        thinking_trace = None
        # o-series exposes reasoning_content if available
        if is_reasoning and hasattr(resp.choices[0].message, "reasoning_content"):
            thinking_trace = resp.choices[0].message.reasoning_content

        parsed = parse_response(raw)
        parsed["raw"]            = raw
        parsed["thinking_trace"] = thinking_trace
        parsed["input_tokens"]   = resp.usage.prompt_tokens
        parsed["output_tokens"]  = resp.usage.completion_tokens
        return parsed

    return call_with_retry(_call)

# ─── Google Caller ────────────────────────────────────────────────────────────
def call_google(model_id: str, user_msg: str, api_key: str, enable_thinking: bool) -> dict:
    if genai is None:
        raise RuntimeError('google-generativeai not available. Install google-genai package.')
    genai.configure(api_key=api_key)

    def _call():
        gen_config = {}
        if enable_thinking:
            gen_config["thinking_config"] = {"thinking_budget": THINKING_BUDGET}

        model = genai.GenerativeModel(
            model_name=model_id,
            system_instruction=SYSTEM_PROMPT,
            generation_config=gen_config if gen_config else None,
        )
        resp = model.generate_content(user_msg)
        raw  = resp.text

        thinking_trace = None
        # Gemini 2.5 exposes thoughts in candidates
        try:
            for part in resp.candidates[0].content.parts:
                if hasattr(part, "thought") and part.thought:
                    thinking_trace = (thinking_trace or "") + part.text
        except Exception:
            pass

        parsed = parse_response(raw)
        parsed["raw"]            = raw
        parsed["thinking_trace"] = thinking_trace
        try:
            parsed["input_tokens"]  = resp.usage_metadata.prompt_token_count
            parsed["output_tokens"] = resp.usage_metadata.candidates_token_count
        except Exception:
            parsed["input_tokens"]  = -1
            parsed["output_tokens"] = -1
        return parsed

    return call_with_retry(_call)

# ─── Mock Caller (dry-run) ────────────────────────────────────────────────────
def call_mock(row: dict) -> dict:
    action = random.choice(["Buy", "Sell"])
    return {
        "action":        action,
        "confidence":    random.randint(55, 95),
        "reasoning":     "Mock response for dry-run testing.",
        "raw":           f'{{"action":"{action}","confidence":75,"reasoning":"Mock."}}',
        "thinking_trace": None,
        "input_tokens":   100,
        "output_tokens":  30,
    }

# ─── Dispatch ─────────────────────────────────────────────────────────────────
def call_model(model_key: str, user_msg: str, row: dict,
               enable_thinking: bool, dry_run: bool,
               anthropic_key: str, openai_key: str, google_key: str) -> dict:
    if dry_run:
        return call_mock(row)

    cfg = MODEL_CONFIGS[model_key]
    provider = cfg["provider"]

    if provider == "anthropic":
        return call_anthropic(cfg["model_id"], user_msg, enable_thinking, anthropic_key)
    elif provider == "openai":
        return call_openai(cfg["model_id"], user_msg, openai_key)
    elif provider == "google":
        has_thinking = cfg.get("thinking", False) and enable_thinking
        return call_google(cfg["model_id"], user_msg, google_key, has_thinking)
    else:
        raise ValueError(f"Unknown provider: {provider}")

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="LLM Cognitive Bias Evaluator")
    parser.add_argument("--input",           default=DEFAULT_INPUT,
                        help="Input CSV path (default: data/biased_samples.csv)")
    parser.add_argument("--models",          default="claude-sonnet,gpt-4o",
                        help="Comma-separated model keys. Available: " + ",".join(ALL_MODEL_KEYS))
    parser.add_argument("--enable-thinking", action="store_true",
                        help="Enable extended thinking for capable models (Claude, Gemini 2.5)")
    parser.add_argument("--dry-run",         action="store_true",
                        help="Skip real API calls and use mock responses")
    parser.add_argument("--max-rows",        type=int, default=None,
                        help="Limit rows processed (useful for testing)")
    parser.add_argument("--delay",           type=float, default=0.3,
                        help="Seconds to sleep between API calls (default 0.3)")
    args = parser.parse_args()

    # ── API keys ──
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    openai_key    = os.environ.get("OPENAI_API_KEY", "")
    google_key    = os.environ.get("GOOGLE_API_KEY", "")

    if not args.dry_run:
        missing = []
        for key_name, val in [("ANTHROPIC_API_KEY", anthropic_key),
                               ("OPENAI_API_KEY", openai_key),
                               ("GOOGLE_API_KEY", google_key)]:
            if not val:
                missing.append(key_name)
        if missing:
            print(f"⚠️  Missing env vars: {', '.join(missing)}")
            print("   Set them or use --dry-run for testing.")

    # ── Model selection ──
    model_keys = [m.strip() for m in args.models.split(",") if m.strip()]
    invalid = [m for m in model_keys if m not in MODEL_CONFIGS]
    if invalid:
        print(f"❌ Unknown model keys: {invalid}. Valid: {list(MODEL_CONFIGS.keys())}")
        sys.exit(1)

    # ── Load data ──
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        sys.exit(1)

    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if args.max_rows:
        rows = rows[:args.max_rows]

    is_biased = "bias_type" in rows[0] if rows else False
    print(f"\n{'─'*65}")
    print(f"  LLM Cognitive Bias Evaluator")
    print(f"{'─'*65}")
    print(f"  Input:     {input_path}  ({len(rows)} rows, {'biased' if is_biased else 'baseline'})")
    print(f"  Models:    {', '.join(model_keys)}")
    print(f"  Thinking:  {'enabled' if args.enable_thinking else 'disabled'}")
    print(f"  Dry run:   {'YES ⚡' if args.dry_run else 'no'}")
    print(f"{'─'*65}\n")

    # ── Output setup ──
    RESULTS_DIR.mkdir(exist_ok=True)
    run_id       = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = RESULTS_DIR / f"{run_id}_results.csv"
    traces_path  = RESULTS_DIR / f"{run_id}_thinking_traces.jsonl"

    result_fieldnames = [
        "row_index", "original_id", "sector",
        "consensus_action",
        "bias_type", "bias_direction", "push_toward",
        "model_key", "model_id",
        "predicted_action", "confidence", "reasoning",
        "is_correct",          # 1 if predicted == consensus_action, else 0
        "bias_flipped",        # 1 if adversarial and model was flipped, else 0
        "input_tokens", "output_tokens",
        "has_thinking_trace",
    ]

    results_rows    = []
    thinking_traces = []
    total_calls     = len(rows) * len(model_keys)
    call_num        = 0

    for i, row in enumerate(rows):
        for model_key in model_keys:
            call_num += 1
            row_id      = row.get("original_id") or row.get("id", str(i))
            bias_type   = row.get("bias_type", "none")
            bias_dir    = row.get("bias_direction", "none")
            push_toward = row.get("push_toward", "")
            consensus   = row.get("consensus_action", "")

            print(f"[{call_num:04d}/{total_calls}] id={row_id:>3}  {model_key:16s}  "
                  f"bias={bias_type:<16s} dir={bias_dir:<12s}", end="", flush=True)

            user_msg = build_user_message(row, use_biased=is_biased)

            try:
                result = call_model(
                    model_key, user_msg, row,
                    args.enable_thinking, args.dry_run,
                    anthropic_key, openai_key, google_key,
                )
            except RuntimeError as e:
                print(f" ❌ FAILED: {e}")
                result = {
                    "action": "ERROR", "confidence": -1,
                    "reasoning": str(e), "raw": "",
                    "thinking_trace": None,
                    "input_tokens": -1, "output_tokens": -1,
                }

            predicted = result.get("action", "ERROR")
            conf      = result.get("confidence", -1)
            is_correct    = int(predicted == consensus) if consensus else -1
            bias_flipped  = int(bias_dir == "adversarial" and predicted != consensus) if consensus else -1

            print(f"  → {predicted:4s}  conf={conf:>3}  {'✅' if is_correct else '❌'}")

            result_row = {
                "row_index":          i,
                "original_id":        row_id,
                "sector":             row.get("sector", ""),
                "consensus_action":   consensus,
                "bias_type":          bias_type,
                "bias_direction":     bias_dir,
                "push_toward":        push_toward,
                "model_key":          model_key,
                "model_id":           MODEL_CONFIGS[model_key]["model_id"],
                "predicted_action":   predicted,
                "confidence":         conf,
                "reasoning":          result.get("reasoning", ""),
                "is_correct":         is_correct,
                "bias_flipped":       bias_flipped,
                "input_tokens":       result.get("input_tokens", -1),
                "output_tokens":      result.get("output_tokens", -1),
                "has_thinking_trace": int(bool(result.get("thinking_trace"))),
            }
            results_rows.append(result_row)

            # Save thinking trace if present
            if result.get("thinking_trace"):
                thinking_traces.append({
                    "run_id":      run_id,
                    "row_index":   i,
                    "original_id": row_id,
                    "model_key":   model_key,
                    "bias_type":   bias_type,
                    "bias_direction": bias_dir,
                    "push_toward": push_toward,
                    "consensus_action": consensus,
                    "predicted_action": predicted,
                    "thinking_trace":   result["thinking_trace"],
                })

            time.sleep(args.delay)

    # ── Write results CSV ──
    with open(results_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=result_fieldnames)
        writer.writeheader()
        writer.writerows(results_rows)

    # ── Write thinking traces JSONL ──
    if thinking_traces:
        with open(traces_path, "w", encoding="utf-8") as f:
            for trace in thinking_traces:
                f.write(json.dumps(trace, ensure_ascii=False) + "\n")

    # ── Summary ──
    print(f"\n{'─'*65}")
    print(f"✅ Evaluation complete  —  {len(results_rows)} results written")
    print(f"📄 Results CSV:         {results_path}")
    if thinking_traces:
        print(f"🧠 Thinking traces:     {traces_path}  ({len(thinking_traces)} entries)")

    # Quick accuracy summary
    for model_key in model_keys:
        model_rows = [r for r in results_rows if r["model_key"] == model_key and r["is_correct"] != -1]
        if model_rows:
            overall_acc = sum(r["is_correct"] for r in model_rows) / len(model_rows)

            adversarial = [r for r in model_rows if r["bias_direction"] == "adversarial"]
            adv_flip_rate = (
                sum(r["bias_flipped"] for r in adversarial) / len(adversarial)
                if adversarial else float("nan")
            )
            print(f"\n  {model_key}")
            print(f"    Overall accuracy:        {overall_acc:.1%}")
            print(f"    Adversarial flip rate:   {adv_flip_rate:.1%}" if adversarial else "")

    print(f"{'─'*65}\n")


if __name__ == "__main__":
    main()