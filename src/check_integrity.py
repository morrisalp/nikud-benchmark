import pandas as pd
from nikud import load_gold, strip_nikud, is_ktiv_match

df = load_gold()

df["stripped"] = df["nikud"].apply(strip_nikud)
df["match"] = df.apply(lambda r: is_ktiv_match(r["plain"], r["stripped"]), axis=1)

duplicates = df[df.duplicated("plain", keep=False)]
mismatches = df[~df["match"]]

print(f"Mismatches: {len(mismatches)}/{len(df)}")
print(f"Duplicates: {df['plain'].duplicated().sum()}")
if not duplicates.empty:
    for plain, count in duplicates["plain"].value_counts().items():
        print(f"  ({count}x) {plain}")

for _, row in mismatches.iterrows():
    plain_words = row["plain"].split()
    stripped_words = row["stripped"].split()
    print(f"\nLine {row.name + 2}:")
    if len(plain_words) == len(stripped_words):
        for i, (pw, sw) in enumerate(zip(plain_words, stripped_words)):
            if not is_ktiv_match(pw, sw):
                print(f"  word {i+1}: {pw} | {sw}")
    else:
        print(f"  plain:   {row['plain']}")
        print(f"  nikud:   {row['nikud']}")
        print(f"  stripped:{row['stripped']}")
