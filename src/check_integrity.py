from collections import Counter
from nikud import load_rows, strip_nikud, is_ktiv_match

rows = load_rows()
mismatches = []

for lineno, plain, with_nikud in rows:
    stripped = strip_nikud(with_nikud)
    if not is_ktiv_match(plain, stripped):
        mismatches.append((lineno, plain, with_nikud, stripped))

plain_counts = Counter(plain for _, plain, _ in rows)
duplicates = [(plain, count) for plain, count in plain_counts.items() if count > 1]

print(f"Mismatches: {len(mismatches)}/{len(rows)}")
print(f"Duplicates: {len(duplicates)}")
for plain, count in duplicates:
    print(f"  ({count}x) {plain}")

for lineno, plain, with_nikud, stripped in mismatches:
    plain_words = plain.split()
    stripped_words = stripped.split()
    print(f"\nLine {lineno}:")
    if len(plain_words) == len(stripped_words):
        for i, (pw, sw) in enumerate(zip(plain_words, stripped_words)):
            if not is_ktiv_match(pw, sw):
                print(f"  word {i+1}: {pw} | {sw}")
    else:
        print(f"  plain:   {plain}")
        print(f"  nikud:   {with_nikud}")
        print(f"  stripped:{stripped}")
