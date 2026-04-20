"""
Compute WER, CER, DER, EM per sample and aggregated, for each model in preds.tsv.

WER/CER are computed two ways:
  - sample-level: average of per-sentence rates
  - corpus-level: errors / total tokens (or chars) across the whole corpus

DER: diacritic error rate = diacritic substitutions / total diacritics in reference
EM:  exact match (1 if pred == ref, else 0)

Outputs:
  output/per_sample_{model}.tsv  — per-sentence metrics + word diffs
  output/aggregated.txt          — aggregated metrics table (also printed to stdout)
"""

import os
import sys
import unicodedata
import pandas as pd
from tabulate import tabulate
sys.path.insert(0, 'src')
from nikud import NIKUD, load_gold

NIKUD_SET = set(NIKUD.keys())
PREDS_PATH = "data/preds.tsv"
OUT_DIR = "output"


def normalize(text: str) -> str:
    """NFC + sort diacritics after each base character for canonical ordering.
    Hebrew combining marks share combining class 220, so NFC leaves their
    relative order undefined — sort them explicitly for stable comparison.
    Also normalizes qamats-katan (U+05C7) → qamats (U+05B8) since some models
    distinguish them but gold does not."""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\u05c7", "\u05b8")
    out = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in NIKUD_SET:
            i += 1
            continue
        diacs, j = [], i + 1
        while j < len(text) and text[j] in NIKUD_SET:
            diacs.append(text[j])
            j += 1
        out.append(ch)
        out.extend(sorted(diacs))
        i = j
    return "".join(out)


# ── metric helpers ─────────────────────────────────────────────────────────────

def levenshtein(a, b):
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[:]
        dp[0] = i
        for j in range(1, n + 1):
            dp[j] = prev[j-1] if a[i-1] == b[j-1] else 1 + min(prev[j], dp[j-1], prev[j-1])
    return dp[n]


def wer_stats(ref, hyp):
    r, h = ref.split(), hyp.split()
    e = levenshtein(r, h)
    return e / len(r) if r else 0.0, e, len(r)


def cer_stats(ref, hyp):
    e = levenshtein(list(ref), list(hyp))
    return e / len(ref) if ref else 0.0, e, len(ref)


def der_stats(ref, hyp):
    def pairs(text):
        result, i = [], 0
        while i < len(text):
            ch = text[i]
            if ch in NIKUD_SET:
                i += 1
                continue
            diacs, j = set(), i + 1
            while j < len(text) and text[j] in NIKUD_SET:
                diacs.add(text[j])
                j += 1
            result.append((ch, diacs))
            i = j
        return result

    rp, hp = pairs(ref), pairs(hyp)
    errors = sum(len(rd.symmetric_difference(hd)) for (_, rd), (_, hd) in zip(rp, hp))
    errors += sum(len(rd) for _, rd in rp[len(hp):])
    total = sum(len(rd) for _, rd in rp)
    return (errors / total if total else 0.0), errors, total


def word_diffs(ref, hyp):
    r_words, h_words = ref.split(), hyp.split()
    diffs = [f"{rw}→{hw}" for rw, hw in zip(r_words, h_words) if rw != hw]
    if len(r_words) != len(h_words):
        diffs.append(f"[word count: {len(r_words)} vs {len(h_words)}]")
    return "  ".join(diffs)


# ── load data ──────────────────────────────────────────────────────────────────

gold = load_gold().set_index("plain")["nikud"].apply(normalize)
preds_df = pd.read_csv(PREDS_PATH, sep="\t", encoding="utf-8", index_col="plain")
preds_df = preds_df.apply(lambda col: col.apply(normalize))
model_names = list(preds_df.columns)

os.makedirs(OUT_DIR, exist_ok=True)

# ── compute metrics and save per-sample TSVs ───────────────────────────────────

agg_rows = []

for m in model_names:
    records = []
    for plain, ref in gold.items():
        hyp = preds_df.loc[plain, m] if plain in preds_df.index else ""
        wr, we, wt = wer_stats(ref, hyp)
        cr, ce, ct = cer_stats(ref, hyp)
        dr, de, dt = der_stats(ref, hyp)
        em = int(ref == hyp)
        records.append({
            "plain": plain, "gold": ref, "pred": hyp,
            "WER": wr, "wer_e": we, "wer_t": wt,
            "CER": cr, "cer_e": ce, "cer_t": ct,
            "DER": dr, "der_e": de, "der_t": dt,
            "EM": em,
            "word_diffs": word_diffs(ref, hyp),
        })

    df = pd.DataFrame(records)
    out_cols = ["plain", "gold", "pred", "WER", "CER", "DER", "EM", "word_diffs"]
    df[out_cols].to_csv(os.path.join(OUT_DIR, f"per_sample_{m}.tsv"), sep="\t", index=False)

    agg_rows.append([
        m,
        f"{df['WER'].mean():.4f}",
        f"{df['wer_e'].sum() / max(df['wer_t'].sum(), 1):.4f}",
        f"{df['CER'].mean():.4f}",
        f"{df['cer_e'].sum() / max(df['cer_t'].sum(), 1):.4f}",
        f"{df['DER'].mean():.4f}",
        f"{df['der_e'].sum() / max(df['der_t'].sum(), 1):.4f}",
        f"{df['EM'].mean():.4f}",
    ])

agg_table = tabulate(
    agg_rows,
    headers=["model", "WER(sample)", "WER(corpus)", "CER(sample)", "CER(corpus)", "DER(sample)", "DER(corpus)", "EM"],
    tablefmt="simple",
)

print(agg_table)
with open(os.path.join(OUT_DIR, "aggregated.txt"), "w", encoding="utf-8") as f:
    f.write(agg_table + "\n")

print(f"\nSaved to {OUT_DIR}/")
