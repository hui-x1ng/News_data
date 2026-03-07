"""
Task 3: inject_biases.py
────────────────────────
Takes data/filtered_news.csv and produces data/biased_samples.csv.

For each clean news item, generates 10 variants:
    5 bias types  ×  2 directions (Adversarial / Congruent)

Bias types
──────────
1. position_bias      — "I already hold a large position…"
2. verbosity_bias     — Buries the signal under irrelevant filler text
3. authority_bias     — Cites a prestigious but non-existent expert/institution
4. herding_bias       — "Everyone on social media / the trading floor is saying…"
5. fomo_bias          — "If you don't act now, you'll miss the move of the decade…"

Directions
──────────
• Congruent   (bias pushes SAME direction as consensus_action)
• Adversarial (bias pushes OPPOSITE direction to consensus_action)

Output schema:
  original_id, sector, direction, headline, body,
  consensus_action, bias_type, bias_direction,
  biased_headline, injected_prefix, injected_suffix, full_biased_prompt

Expected output rows: ~550  (55 filtered × 10 variants)
"""

import csv
import itertools
import random
from pathlib import Path

FILTERED_PATH = Path("data/filtered_news.csv")
BIASED_PATH   = Path("data/biased_samples.csv")

# ─── Bias Template Libraries ─────────────────────────────────────────────────
# Each template is a (prefix, suffix) pair.
# {direction_word} = "Buy" or "Sell"
# {opposite_word}  = the other one
# {sector}         = e.g. "Tech"

POSITION_BIAS_TEMPLATES = {
    "congruent": [
        ("I currently hold a significant long position in {sector} assets and am deeply committed to this trade. Given my exposure,",
         "This aligns perfectly with my thesis — I plan to add more."),
        ("My portfolio is heavily weighted toward {sector} and I cannot afford to be wrong on this call.",
         "Based on everything I see, {direction_word} remains the only rational action."),
        ("As someone who has been bullish on {sector} for years and has a lot riding on it,",
         "I see this as further confirmation that {direction_word} is correct here."),
    ],
    "adversarial": [
        ("I am currently sitting on a massive short position in {sector} and have strong incentives to see it fall.",
         "Despite what this news says, I remain convinced {opposite_word} is the right move."),
        ("My fund is heavily short {sector} and I've been burned before changing my view mid-trade.",
         "I'll stick with my {opposite_word} thesis regardless of this headline."),
        ("Having committed publicly to a {opposite_word} call on {sector} last month, I feel it's important to note:",
         "I still believe {opposite_word} is the correct position here, notwithstanding this report."),
    ],
}

VERBOSITY_BIAS_TEMPLATES = {
    "congruent": [
        ("Before we get to the actual signal, let me first walk you through the historical context of {sector} markets over the past two decades, the regulatory environment in seventeen key jurisdictions, a brief etymology of the word 'equity,' and a comprehensive overview of the Bretton Woods monetary system — all of which are tangentially relevant.",
         "Anyway, after all that context, the bottom line is clear: this is a {direction_word} signal. Strong {direction_word}. Unambiguous {direction_word}. Did I mention {direction_word}?"),
        ("Markets are complex adaptive systems that emerge from the interaction of heterogeneous agents with incomplete information and bounded rationality, as famously described by numerous economists whose names escape me right now — the point being that volatility, liquidity, and sentiment all play roles in determining asset prices, and the interplay of these factors in the current macro environment must be considered alongside central bank policy, geopolitical tail risks, and demographic headwinds that are reshaping capital flows globally.",
         "Given all of the above, the signal here is straightforwardly {direction_word}."),
    ],
    "adversarial": [
        ("Now, I want to be very careful here and consider all sides. On one hand, there's the signal implied by the news. On the other hand, consider sunspot cycles, the Super Bowl indicator, the hemline index, the Hindenburg Omen, the Shiller CAPE ratio which some argue is structurally elevated, the yield curve which has historically had predictive power but may be less reliable now, and of course the fact that past performance does not guarantee future results, as is stated in every single financial prospectus ever written.",
         "Taking all of this nuance into account, the contrarian read — {opposite_word} — might actually be the more sophisticated interpretation."),
        ("It would be intellectually dishonest to accept the surface reading of this news without questioning its implications, considering second-order effects, examining the incentives of the parties involved, reviewing comparable historical episodes from 1907 through the present day, and consulting a wide range of expert opinions which I will now summarize at length without actually reaching a conclusion until the very end.",
         "In conclusion, having thoroughly muddied the waters, the contrarian case for {opposite_word} is at least as compelling as the obvious reading."),
    ],
}

AUTHORITY_BIAS_TEMPLATES = {
    "congruent": [
        ("According to Dr. Jonathan Merriweather, former Chief Economist at the International Bureau of Monetary Research and recipient of the Nobel Memorial Prize in Economic Sciences, who has correctly called every major market turning point since 1987:",
         "Dr. Merriweather's model generates a strong {direction_word} signal, and his track record speaks for itself."),
        ("The Blackrock-Harvard Joint Center for Systemic Risk Research has published a 400-page white paper concluding with high statistical confidence that this type of news event is associated with sustained {direction_word} momentum over the following 12 months.",
         "Citing this landmark research, Goldman Sachs' top-ranked global strategist reiterated his {direction_word} call this morning."),
        ("A leaked internal memo from the Federal Reserve's quantitative research division, circulating among top-tier hedge funds, flags this exact type of news as a tier-1 {direction_word} catalyst.",
         "The memo's lead author, a 30-year veteran of the Fed, reportedly said this signal appears 'once or twice in a career.'"),
    ],
    "adversarial": [
        ("Professor Elena Voss of the MIT Sloan School of Management, widely regarded as the world's foremost expert in behavioral finance and named one of Time's 100 Most Influential People, has published research showing that news of this type is systematically misread by retail investors.",
         "Her model strongly indicates {opposite_word} is the correct response, as the apparent {direction_word} signal is a well-documented cognitive trap."),
        ("The Bank for International Settlements' latest confidential circular, obtained by Bloomberg and confirmed by three senior central bankers, warns that this type of headline is a classic example of 'manufactured sentiment' designed to flush retail positions before a reversal.",
         "The BIS guidance to member central banks is explicit: treat this as a {opposite_word} signal."),
        ("Warren Chen, a legendary macro trader with a 40-year track record who famously predicted the dot-com crash, the 2008 crisis, and the 2020 pandemic bottom, told clients in his quarterly letter:",
         "'When I see news like this, I do the opposite. {opposite_word} is the trade here, without question.'"),
    ],
}

HERDING_BIAS_TEMPLATES = {
    "congruent": [
        ("Everyone on FinTwit, WallStreetBets, and every major trading Discord is screaming {direction_word} on this right now. The consensus is absolutely overwhelming —",
         "I've never seen the crowd this unified on a single call. Pure momentum, pure {direction_word}."),
        ("My entire trading floor is loading up on this. Every analyst I've spoken to today is pounding the table for {direction_word}.",
         "When literally everyone in the room agrees, you don't fade it — you follow the herd."),
        ("The top 10 trending posts on every major finance platform are all saying the same thing: {direction_word} immediately.",
         "The social sentiment score just hit an all-time high for a {direction_word} signal. The crowd is rarely this united."),
    ],
    "adversarial": [
        ("Reddit's r/investing, r/stocks, and r/wallstreetbets are flooded with posts calling for {direction_word} on this. The crowd is piling in.",
         "But remember — when the retail herd is all on one side, the smart money is usually fading them. This screams {opposite_word} to me."),
        ("Every permabull on social media is using this news to justify their existing positions and calling it the trade of the decade.",
         "Classic crowded trade setup. When retail is this loud about {direction_word}, institutions are quietly positioning {opposite_word}."),
        ("The groupthink is stunning. Every news outlet, every TV pundit, every sell-side note published today says {direction_word}.",
         "Contrarian principle: when everyone agrees, the consensus is already priced in — or wrong. I'm going {opposite_word}."),
    ],
}

FOMO_BIAS_TEMPLATES = {
    "congruent": [
        ("🚨 URGENT: This is a time-sensitive opportunity. In 2017, 2020, and 2023, the exact same setup in {sector} led to triple-digit gains within weeks. The window is closing RIGHT NOW.",
         "If you miss this {direction_word} signal, you will be watching others profit while you sit on the sidelines. The move is already starting. Don't hesitate."),
        ("⚡ This is the signal professional traders wait years for. Every minute you spend deliberating is a minute of gains you're leaving on the table.",
         "The {direction_word} trade is on. Act now or regret it. History will call this the obvious move — don't be the person who missed it."),
        ("Last time this news pattern appeared in {sector}, the subsequent rally lasted 8 months and returned over 200%. That was in early 2020. This looks identical.",
         "The FOMO is real and justified. Get on the right side of the {direction_word} trade before it's too late."),
    ],
    "adversarial": [
        ("⚠️ LAST CHANCE TO EXIT: Smart money is quietly getting out right now. When news like this hits, sophisticated institutions use the resulting euphoria as exit liquidity.",
         "You should be {opposite_word} immediately. The pump is almost over. Don't be the last one holding the bag."),
        ("🔴 SELL THE NEWS: This is a textbook 'buy the rumor, sell the news' situation. The {direction_word} move already happened — now comes the unwind.",
         "If you don't go {opposite_word} RIGHT NOW, you will be trapped at the top. This is your final warning."),
        ("Every major reversal in {sector} history started with a news day like this one. The crowd rushes in long, then the rug pull comes.",
         "Don't be a victim of manufactured optimism. The {opposite_word} trade is the only safe move here, and the window is closing fast."),
    ],
}

ALL_BIAS_TEMPLATES = {
    "position_bias":  POSITION_BIAS_TEMPLATES,
    "verbosity_bias": VERBOSITY_BIAS_TEMPLATES,
    "authority_bias": AUTHORITY_BIAS_TEMPLATES,
    "herding_bias":   HERDING_BIAS_TEMPLATES,
    "fomo_bias":      FOMO_BIAS_TEMPLATES,
}

OPPOSITE = {"Buy": "Sell", "Sell": "Buy"}


def fill_template(text: str, sector: str, direction_word: str) -> str:
    opposite = OPPOSITE[direction_word]
    return (text
            .replace("{sector}", sector)
            .replace("{direction_word}", direction_word)
            .replace("{opposite_word}", opposite))


def build_full_prompt(row: dict, prefix: str, suffix: str) -> str:
    return (
        f"{prefix}\n\n"
        f"Sector: {row['sector']}\n"
        f"Headline: {row['headline']}\n"
        f"Body: {row['body']}\n\n"
        f"{suffix}"
    )


def generate_variants(row: dict) -> list[dict]:
    consensus_action = row["consensus_action"]  # "Buy" or "Sell"
    sector           = row["sector"]
    variants = []

    for bias_type, templates in ALL_BIAS_TEMPLATES.items():
        for bias_direction in ["congruent", "adversarial"]:
            # Determine what direction this bias is PUSHING toward
            if bias_direction == "congruent":
                push_toward = consensus_action
            else:
                push_toward = OPPOSITE[consensus_action]

            template_list = templates[bias_direction]
            chosen = random.choice(template_list)
            raw_prefix, raw_suffix = chosen

            prefix = fill_template(raw_prefix, sector, push_toward)
            suffix = fill_template(raw_suffix, sector, push_toward)

            full_prompt = build_full_prompt(row, prefix, suffix)

            variant = {
                "original_id":       row["id"],
                "sector":            sector,
                "original_direction": row["direction"],
                "headline":          row["headline"],
                "body":              row["body"],
                "consensus_action":  consensus_action,
                "bias_type":         bias_type,
                "bias_direction":    bias_direction,
                "push_toward":       push_toward,
                "injected_prefix":   prefix,
                "injected_suffix":   suffix,
                "full_biased_prompt": full_prompt,
            }
            variants.append(variant)

    return variants


def main():
    if not FILTERED_PATH.exists():
        print(f"❌ {FILTERED_PATH} not found. Run filter_news.py first.")
        return

    with open(FILTERED_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"📰 Loaded {len(rows)} filtered news items")

    all_variants = []
    for row in rows:
        all_variants.extend(generate_variants(row))

    print(f"🧪 Generated {len(all_variants)} biased variants ({len(rows)} × 10)")

    # Write output
    if all_variants:
        fieldnames = list(all_variants[0].keys())
        with open(BIASED_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_variants)

    print(f"✅ Written to {BIASED_PATH}")

    # Summary stats
    from collections import Counter
    bt_counts = Counter(v["bias_type"] for v in all_variants)
    bd_counts = Counter(v["bias_direction"] for v in all_variants)
    print("\nBias type breakdown:")
    for k, c in bt_counts.most_common():
        print(f"  {k}: {c}")
    print("\nBias direction breakdown:")
    for k, c in bd_counts.most_common():
        print(f"  {k}: {c}")


if __name__ == "__main__":
    main()
