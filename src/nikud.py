NIKUD = {
    "\u05b0": "shva",
    "\u05b1": "reduced-segol",
    "\u05b2": "reduced-patah",
    "\u05b3": "reduced-qamats",
    "\u05b4": "hiriq",
    "\u05b5": "tsere",
    "\u05b6": "segol",
    "\u05b7": "patah",
    "\u05b8": "qamats",
    "\u05b9": "holam",
    "\u05ba": "holam-vav",
    "\u05bb": "qubuts",
    "\u05bc": "dagesh",
    "\u05bd": "meteg",
    "\u05be": "maqaf",
    "\u05bf": "rafe",
    "\u05c0": "paseq",
    "\u05c1": "shin-dot",
    "\u05c2": "sin-dot",
    "\u05c3": "sof-pasuq",
    "\u05c4": "upper-dot",
    "\u05c5": "lower-dot",
    "\u05c6": "nun-hafukha",
    "\u05c7": "qamats-qatan",
    "\u05f3": "geresh",
    "\u05f4": "gershayim",
}

YUD = "\u05d9"
VAV = "\u05d5"

DATA_PATH = "data/gold.tsv"


def strip_nikud(text):
    return "".join(c for c in text if c not in NIKUD)


def load_gold():
    import pandas as pd
    return pd.read_csv(DATA_PATH, sep="\t", encoding="utf-8")


def is_ktiv_match(plain, nikud_stripped):
    i, j = 0, 0
    while i < len(plain) and j < len(nikud_stripped):
        if plain[i] == nikud_stripped[j]:
            i += 1
            j += 1
        elif nikud_stripped[j] in (YUD, VAV):
            j += 1
        elif plain[i] in (YUD, VAV):
            i += 1
        else:
            return False
    while i < len(plain) and plain[i] in (YUD, VAV):
        i += 1
    while j < len(nikud_stripped) and nikud_stripped[j] in (YUD, VAV):
        j += 1
    return i == len(plain) and j == len(nikud_stripped)
