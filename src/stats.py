import pandas as pd
from collections import Counter
from nikud import NIKUD, load_gold

df = load_gold()
total = len(df)
word_counts = df["plain"].str.split().str.len()
total_words = word_counts.sum()

diacritic_counts: Counter = Counter()
for text in df["nikud"]:
    for c in text:
        if c in NIKUD:
            diacritic_counts[c] += 1

print(f"Rows:             {total}")
print(f"Total words:      {total_words}")
print(f"Avg length:       {df['plain'].str.len().mean():.1f} chars / {word_counts.mean():.1f} words (plain)")
print(f"Total diacritics: {sum(diacritic_counts.values())}")
print()
print("Diacritics by type:")
for c, count in sorted(diacritic_counts.items(), key=lambda x: -x[1]):
    print(f"  {NIKUD[c]:<18} {count:>6}")
