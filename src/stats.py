from collections import Counter
from nikud import NIKUD, load_rows

rows = load_rows()
total = len(rows)
total_chars = sum(len(plain) for _, plain, _ in rows)
total_words = sum(len(plain.split()) for _, plain, _ in rows)

diacritic_counts: Counter = Counter()
for _, _, nikud in rows:
    for c in nikud:
        if c in NIKUD:
            diacritic_counts[c] += 1

print(f"Rows:             {total}")
print(f"Total words:      {total_words}")
print(f"Avg length:       {total_chars/total:.1f} chars / {total_words/total:.1f} words (plain)")
print(f"Total diacritics: {sum(diacritic_counts.values())}")
print()
print("Diacritics by type:")
for c, count in sorted(diacritic_counts.items(), key=lambda x: -x[1]):
    print(f"  {NIKUD[c]:<18} {count:>6}")
