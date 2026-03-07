"""
Task 2: filter_news.py
─────────────────────
Feeds each row of base_news.csv to three "judge" LLMs:
  • Claude  (claude-sonnet-4-20250514  via Anthropic API)
  • GPT-4o  (gpt-4o-2024-11-20         via OpenAI API)
  • Gemini  (gemini-2.0-flash          via Google Generative Language API)

Retention rule (strict):
  • All three models must agree on the same Action (Buy / Sell)
  • All three models must report Confidence >= 70

Output: data/filtered_news.csv  (expected ~50-60 rows after filtering)
        data/filter_raw_responses.jsonl  (full model responses for audit)

Usage (推荐):
    把 .env 放在项目根目录，脚本会自动读取。
    或者手动 export:
    export ANTHROPIC_API_KEY="sk-ant-..."
    export OPENAI_API_KEY="sk-..."
    export GOOGLE_API_KEY="AI..."   # 若 Gemini Key 失效可暂时跳过
    python scripts/filter_news.py

    若只想用 Anthropic + OpenAI（跳过 Gemini），在 main() 中把
    callers 列表里的 gemini 条目注释掉即可。
"""

import csv
import json
import os
import re
import time
import random
from pathlib import Path

# Auto-load .env from project root (works without python-dotenv)
def _load_env():
    for candidate in [Path(".env"), Path(__file__).parent.parent / ".env"]:
        if candidate.exists():
            for line in candidate.read_text(encoding='utf-8').splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())
            break
_load_env()

import anthropic
import openai
import google.generativeai as genai

# ─── Config ──────────────────────────────────────────────────────────────────
BASE_NEWS_PATH   = Path("data/base_news.csv")
FILTERED_PATH    = Path("data/filtered_news.csv")
RAW_LOG_PATH     = Path("data/filter_raw_responses.jsonl")
MIN_CONFIDENCE   = 70
MAX_RETRIES      = 5

ANTHROPIC_KEY    = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_KEY       = os.environ.get("OPENAI_API_KEY", "")
GOOGLE_KEY       = os.environ.get("GOOGLE_API_KEY", "")

# ─── Shared Prompt Template ───────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a professional financial analyst. You will be given a news headline and body. Your job is to determine whether this news is a BUY signal or SELL signal for the affected sector/asset.

Respond ONLY in this exact JSON format (no markdown, no extra text):
{
  "action": "Buy" or "Sell",
  "confidence": <integer 0-100>,
  "reasoning": "<one concise sentence explaining why>"
}"""

def make_user_prompt(row: dict) -> str:
    return f"""Sector: {row['sector']}
Direction hint: [REDACTED]
Headline: {row['headline']}
Body: {row['body']}

What is your trading signal? Respond in JSON only."""

# ─── Exponential Back-off Retry ───────────────────────────────────────────────
def retry_with_backoff(fn, max_retries=MAX_RETRIES):
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            wait = (2 ** attempt) + random.uniform(0, 1)
            print(f"    ⚠️  Error: {e}  — retrying in {wait:.1f}s (attempt {attempt+1}/{max_retries})")
            time.sleep(wait)
    raise RuntimeError(f"Failed after {max_retries} retries")

# ─── JSON Parser (robust) ─────────────────────────────────────────────────────
def parse_json_response(text: str) -> dict:
    # Strip markdown fences if present
    text = re.sub(r"```json|```", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Attempt regex extraction
        m = re.search(r'\{.*?"action".*?\}', text, re.DOTALL)
        if m:
            return json.loads(m.group())
        raise

# ─── Model Callers ────────────────────────────────────────────────────────────
def call_claude(row: dict) -> dict:
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    def _call():
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": make_user_prompt(row)}],
        )
        raw = resp.content[0].text
        parsed = parse_json_response(raw)
        parsed["raw"] = raw
        return parsed
    return retry_with_backoff(_call)


def call_gpt(row: dict) -> dict:
    client = openai.OpenAI(api_key=OPENAI_KEY)
    def _call():
        resp = client.chat.completions.create(
            model="gpt-4o-2024-11-20",
            max_tokens=256,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": make_user_prompt(row)},
            ],
            temperature=0,
        )
        raw = resp.choices[0].message.content
        parsed = parse_json_response(raw)
        parsed["raw"] = raw
        return parsed
    return retry_with_backoff(_call)


def call_gemini(row: dict) -> dict:
    genai.configure(api_key=GOOGLE_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=SYSTEM_PROMPT,
    )
    def _call():
        resp = model.generate_content(make_user_prompt(row))
        raw = resp.text
        parsed = parse_json_response(raw)
        parsed["raw"] = raw
        return parsed
    return retry_with_backoff(_call)


# ─── Main Filtering Loop ──────────────────────────────────────────────────────
def main():
    if not all([ANTHROPIC_KEY, OPENAI_KEY, GOOGLE_KEY]):
        print("❌ Missing API keys. Set ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY.")
        return

    with open(BASE_NEWS_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"📰 Loaded {len(rows)} news items from {BASE_NEWS_PATH}\n")

    filtered_rows = []
    raw_log = []

    for i, row in enumerate(rows):
        print(f"[{i+1:02d}/{len(rows)}] {row['sector']:12s} | {row['direction']:8s} | {row['headline'][:60]}…")

        results = {}
        ok = True

        for model_name, caller in [("claude", call_claude), ("gpt", call_gpt)]:
            try:
                res = caller(row)
                results[model_name] = res
                action_str = res.get("action", "?")
                conf_str   = res.get("confidence", "?")
                print(f"    {model_name:8s} → {action_str:4s}  conf={conf_str}")
            except Exception as e:
                print(f"    {model_name:8s} → FAILED: {e}")
                ok = False
                break

        if not ok:
            raw_log.append({"id": row["id"], "results": results, "kept": False, "reason": "model_failure"})
            continue

        # Consensus check
        actions     = [r["action"] for r in results.values()]
        confidences = [r.get("confidence", 0) for r in results.values()]

        all_agree       = len(set(actions)) == 1
        all_confident   = all(c >= MIN_CONFIDENCE for c in confidences)

        if all_agree and all_confident:
            row["consensus_action"]    = actions[0]
            row["claude_confidence"]   = results["claude"]["confidence"]
            row["gpt_confidence"]      = results["gpt"]["confidence"]
            #row["gemini_confidence"]   = results["gemini"]["confidence"]
            row["claude_reasoning"]    = results["claude"].get("reasoning", "")
            row["gpt_reasoning"]       = results["gpt"].get("reasoning", "")
            #row["gemini_reasoning"]    = results["gemini"].get("reasoning", "")
            filtered_rows.append(row)
            print(f"    ✅ KEPT  (consensus={actions[0]}, conf={confidences})")
        else:
            reason = "no_consensus" if not all_agree else "low_confidence"
            print(f"    ❌ DROPPED ({reason}, actions={actions}, conf={confidences})")
            raw_log.append({"id": row["id"], "results": results, "kept": False, "reason": reason})
            continue

        raw_log.append({"id": row["id"], "results": results, "kept": True})
        time.sleep(0.5)  # gentle rate limiting

    # Write filtered CSV
    if filtered_rows:
        fieldnames = list(filtered_rows[0].keys())
        with open(FILTERED_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered_rows)

    # Write raw log
    with open(RAW_LOG_PATH, "w", encoding="utf-8") as f:
        for entry in raw_log:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"\n{'─'*60}")
    print(f"✅ Filtered {len(filtered_rows)} / {len(rows)} items kept")
    print(f"📄 Filtered CSV  → {FILTERED_PATH}")
    print(f"📄 Raw responses → {RAW_LOG_PATH}")


if __name__ == "__main__":
    main()
