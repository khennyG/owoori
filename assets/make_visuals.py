"""The figures, hand-built SVG. Plum-and-gold: the colour of money."""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

GROUND = "#141019"
PANEL = "#1E1826"
INK = "#F0EBE3"
DIM = "#9A8FA6"
GRID = "#2B2336"
GOLD = "#E8B04B"
CORAL = "#E8654F"
TEAL = "#4FBFA8"
VIOLET = "#9F7FE8"
SERIF = "'Iowan Old Style', Palatino, Georgia, serif"
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

import html as _html

STORY = json.loads((ROOT / "assets" / "story.json").read_text())


def esc(s):
    return _html.escape(str(s), quote=True)


def T(x, y, s, size=12, fill=INK, anchor="start", weight="normal",
      family=None, op=1.0, ls=None):
    a = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'font-size="{size}"',
         f'fill="{fill}"', f'text-anchor="{anchor}"']
    if weight != "normal":
        a.append(f'font-weight="{weight}"')
    if family:
        a.append(f'font-family="{family}"')
    if op != 1:
        a.append(f'opacity="{op}"')
    if ls:
        a.append(f'letter-spacing="{ls}"')
    return f'<text {" ".join(a)}>{esc(s)}</text>'


def L(x1, y1, x2, y2, stroke=GRID, w=1.0, op=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{w}" opacity="{op}"{d}/>')


def R(x, y, w, h, fill, op=1.0, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w,0):.1f}" '
            f'height="{max(h,0):.1f}" fill="{fill}" opacity="{op}" rx="{rx}"/>')


def C(cx, cy, r, fill, op=1.0, stroke=None, sw=1):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" '
            f'opacity="{op}"{s}/>')


def head(W, H, title, sub, kicker):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}">',
        R(0, 0, W, H, GROUND),
        T(40, 42, kicker, 11, DIM, ls=2.2),
        T(40, 80, title, 29, INK, family=SERIF),
        T(40, 106, sub, 13, DIM),
    ]


def close(p, name):
    p.append("</svg>")
    (ROOT / "assets" / name).write_text("\n".join(p))
    print(name)


# ----------------------------------------------------------------- the atlas

def fig_atlas():
    langs = STORY["languages_ranked"]          # sorted worst-first
    W, H = 1320, 860
    Lm, Rm, Tm, Bm = 110, 1120, 200, 620
    n = len(langs)
    lo, hi = 1.0, 13.5

    def X(i):
        return Lm + (Rm - Lm) * i / (n - 1)

    def Y(v):
        import math
        return Bm - (Bm - Tm) * (math.log(min(max(v, lo), hi)) - 0) / \
            (math.log(hi))

    p = head(W, H, "What 204 languages pay for the same sentences",
             "Median premium across the frontier tokenizers (GPT-3.5/4, "
             "GPT-4o, Qwen2.5) on identical parallel content. English pays 1.",
             "OWOORI  /  THE ATLAS")

    for v in (1, 2, 3, 5, 8, 13):
        p.append(L(Lm - 10, Y(v), Rm, Y(v), GRID, 1, 0.55, dash="2 6"))
        p.append(T(Lm - 18, Y(v) + 4, f"{v}x", 11, DIM, anchor="end"))

    highlight = {"eng_Latn": ("English", TEAL), "yor_Latn": ("Yoruba", GOLD),
                 "amh_Ethi": ("Amharic", CORAL), "swh_Latn": ("Swahili", GOLD),
                 "hin_Deva": ("Hindi", VIOLET), "cmn_Hans": ("Mandarin", VIOLET),
                 "sat_Olck": ("Santali", CORAL), "mya_Mymr": ("Burmese", CORAL),
                 "fra_Latn": ("French", TEAL), "tam_Taml": ("Tamil", VIOLET)}

    for i, x in enumerate(reversed(langs)):       # cheapest on the left
        v = x["frontier_premium"]
        colour = TEAL if v < 1.6 else (GOLD if v < 3 else CORAL)
        p.append(C(X(i), Y(v), 3.2, colour, 0.75))
    offsets = {"eng_Latn": (0, 24, "middle"), "mya_Mymr": (-64, 4, "end"),
               "tam_Taml": (-14, -16, "end"), "amh_Ethi": (14, 12, "start"),
               "sat_Olck": (-10, -16, "end"), "hin_Deva": (-14, -14, "end")}
    for i, x in enumerate(reversed(langs)):
        if x["code"] in highlight:
            name, colour = highlight[x["code"]]
            v = x["frontier_premium"]
            p.append(C(X(i), Y(v), 5.2, colour, 1.0, stroke=INK, sw=1.2))
            dx, dy, anc = offsets.get(x["code"], (0, -14, "middle"))
            p.append(T(X(i) + dx, Y(v) + dy, f"{name} {v:.1f}x", 11.5, colour,
                       anchor=anc))

    p.append(T((Lm + Rm) / 2, Bm + 30,
               "the 204 languages of FLORES-200, cheapest to costliest",
               11, DIM, anchor="middle"))

    share2 = sum(1 for x in langs if x["frontier_premium"] > 2) / n
    share4 = sum(1 for x in langs if x["frontier_premium"] > 4) / n
    ny = Bm + 66
    p.append(R(90, ny - 22, 1140, 108, PANEL, 0.6, rx=4))
    p.append(T(114, ny, "READING THE ATLAS", 10.5, DIM, ls=1.8))
    for i, s in enumerate([
            f"{share2:.0%} of the languages pay more than double English's rate; {share4:.0%} pay more than four times. The steep right",
            "wall is almost entirely non-Latin scripts: Ol Chiki, Tifinagh, Myanmar, Tibetan, Odia, Ge'ez. For them the tokenizer",
            "falls back to spending roughly one token per byte, and their scripts cost three bytes per character in UTF-8."]):
        p.append(T(114, ny + 24 + i * 21, s, 12, INK if i == 0 else DIM))
    close(p, "atlas.svg")


# ------------------------------------------------------------ design choices

def fig_design():
    ts = STORY["tokenizer_stats"]
    order = sorted(ts.items(), key=lambda kv: kv[1]["median_premium"])
    W, H = 1320, 830
    Lm, Rm, Tm = 300, 1130, 210
    row_h = 40
    lo, hi = 1.0, 14.0

    def X(v):
        import math
        return Lm + (Rm - Lm) * math.log(min(max(v, lo), hi)) / math.log(hi)

    p = head(W, H, "The tax is a design choice",
             "Median, 90th percentile and worst-case premium across all 204 "
             "languages, per tokenizer. Log scale.",
             "OWOORI  /  TWELVE TOKENIZERS, RANKED BY FAIRNESS")

    for v in (1, 2, 4, 8, 13):
        p.append(L(X(v), Tm - 16, X(v), Tm + len(order) * row_h + 6, GRID, 1,
                   0.5, dash="2 6"))
        p.append(T(X(v), Tm - 24, f"{v}x", 10.5, DIM, anchor="middle"))

    fam_colour = {"English-centric BPE": CORAL, "frontier BPE": GOLD,
                  "multilingual by design": TEAL}
    for i, (name, s) in enumerate(order):
        y = Tm + i * row_h + row_h / 2
        colour = fam_colour[s["family"]]
        p.append(T(Lm - 14, y + 4, name, 12.5, INK, anchor="end"))
        p.append(L(X(s["median_premium"]), y, X(s["max_premium"]), y,
                   colour, 2.0, 0.55))
        p.append(C(X(s["median_premium"]), y, 6.0, colour))
        p.append(C(X(s["p90_premium"]), y, 3.6, colour, 0.85))
        p.append(C(X(s["max_premium"]), y, 3.0, colour, 0.0, stroke=colour,
                   sw=1.6))
        p.append(T(X(s["max_premium"]) + 10, y + 4,
                   f"worst: {s['max_premium']:.1f}x", 9.5, DIM))

    ky = Tm + len(order) * row_h + 40
    for j, (fam, colour) in enumerate(fam_colour.items()):
        p.append(C(120 + j * 300 + 5, ky - 4, 5, colour))
        p.append(T(120 + j * 300 + 18, ky, fam, 11, DIM))
    p.append(T(120, ky + 34,
               "solid dot = median, small dot = 90th percentile, ring = the "
               "single worst language", 11, DIM))
    p.append(T(120, ky + 56,
               "on the median, every multilingual-by-design tokenizer beats "
               "every English-centric one; on the worst case, BLOOM's 12.6x "
               "shows intent alone is not enough:", 12, INK))
    p.append(T(120, ky + 76,
               "its vocabulary covered 46 languages and the languages outside "
               "that set still fall to bytes", 12, INK))
    close(p, "design.svg")


# ---------------------------------------------------------- the big languages

def fig_bigmoney():
    big = sorted(STORY["big_languages"], key=lambda x: -x["o200k"])
    W = 1320
    row_h = 26
    Tm = 210
    H = Tm + len(big) * row_h + 170
    Lm, Rm = 260, 1140
    hi = 6.2

    def X(v):
        return Lm + (Rm - Lm) * min(v, hi) / hi

    p = head(W, H, "What the world's big languages pay",
             "Premium under the GPT-4o tokenizer for identical content, "
             "for two dozen of the most spoken languages.",
             "OWOORI  /  BILLIONS OF SPEAKERS, ONE METER")

    for v in (1, 2, 3, 4, 5, 6):
        p.append(L(X(v), Tm - 12, X(v), Tm + len(big) * row_h + 4, GRID, 1,
                   0.5, dash="2 6"))
        p.append(T(X(v), Tm - 20, f"{v}x", 10.5, DIM, anchor="middle"))
    p.append(L(X(1), Tm - 12, X(1), Tm + len(big) * row_h + 4, TEAL, 1.4, 0.8))

    for i, x in enumerate(big):
        y = Tm + i * row_h + row_h / 2
        v = x["o200k"]
        colour = TEAL if v < 1.5 else (GOLD if v < 2.5 else CORAL)
        p.append(T(Lm - 14, y + 4, x["name"], 12, INK, anchor="end"))
        p.append(T(Lm - 120, y + 4, f"{x['speakers_m']:,}M", 9.5, DIM,
                   anchor="end"))
        p.append(R(X(1) if v >= 1 else X(v), y - 7,
                   abs(X(v) - X(1)), 14, colour, 0.9, rx=2))
        p.append(T(X(v) + 8, y + 4, f"{v:.2f}x", 10.5, colour))

    ny = Tm + len(big) * row_h + 36
    p.append(T(260, ny,
               "speaker counts at the far left (first plus second language, "
               "rough public figures). The premium multiplies API price,",
               11.5, DIM))
    p.append(T(260, ny + 20,
               "latency and context shrinkage at once, so a Yoruba or Amharic "
               "product pays it three ways simultaneously.", 11.5, DIM))
    close(p, "bigmoney.svg")


# ----------------------------------------------------- the diacritic surcharge

def fig_surcharge():
    ds = STORY["diacritic_surcharge"]
    order = sorted(ds.items(), key=lambda kv: -kv[1]["surcharge"])
    W, H = 1320, 880
    Lm, Tm = 320, 220
    row_h = 40

    def X(v):
        return Lm + 620 * (min(v, 1.8) - 1.0) / 0.8

    p = head(W, H, "The surcharge for writing Yoruba correctly",
             "Tokens for the same 1,012 sentences with their tone and "
             "dot-below marks, relative to the same text stripped bare.",
             "OWOORI  /  THE ORTHOGRAPHY PENALTY")

    for v in (1.0, 1.2, 1.4, 1.6, 1.8):
        p.append(L(X(v), Tm - 14, X(v), Tm + len(order) * row_h + 6, GRID, 1,
                   0.5, dash="2 6"))
        p.append(T(X(v), Tm - 22, f"{v:.1f}x", 10.5, DIM, anchor="middle"))
    p.append(L(X(1.0), Tm - 14, X(1.0), Tm + len(order) * row_h + 6, TEAL,
               1.4, 0.9))

    for i, (name, d) in enumerate(order):
        y = Tm + i * row_h + row_h / 2
        v = d["surcharge"]
        colour = CORAL if v > 1.4 else (GOLD if v > 1.15 else TEAL)
        p.append(T(Lm - 14, y + 4, name, 12.5, INK, anchor="end"))
        p.append(R(X(1.0), y - 8, X(v) - X(1.0), 16, colour, 0.9, rx=2))
        p.append(T(X(v) + 8, y + 4, f"+{100*(v-1):.0f}%", 11, colour))

    ny = Tm + len(order) * row_h + 40
    p.append(R(90, ny - 22, 1140, 112, PANEL, 0.6, rx=4))
    p.append(T(114, ny, "WHY THIS ONE STINGS", 10.5, DIM, ls=1.8))
    for i, s in enumerate([
            "The marks are not decoration: they are what makes Yoruba readable (my ami project restores them). Every tokenizer",
            "here charges extra for the marked text, up to double under GPT-2, so the incentive runs against writing the language",
            "correctly. A Yoruba speaker is taxed once for their language and a second time for their orthography."]):
        p.append(T(114, ny + 24 + i * 21, s, 12, INK if i == 2 else DIM))
    close(p, "surcharge.svg")


FIGURES = [fig_atlas, fig_design, fig_bigmoney, fig_surcharge]

if __name__ == "__main__":
    want = sys.argv[1:]
    for f in FIGURES:
        if not want or f.__name__.replace("fig_", "") in want:
            f()
