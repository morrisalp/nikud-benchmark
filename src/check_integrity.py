from nikud import load_rows, strip_nikud, is_ktiv_match

rows = load_rows()
mismatches = []

for lineno, plain, with_nikud in rows:
    stripped = strip_nikud(with_nikud)
    if not is_ktiv_match(plain, stripped):
        mismatches.append((lineno, plain, with_nikud, stripped))

print(f"Mismatches: {len(mismatches)}/{len(rows)}")

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
