"""From 2,448 measurements to the story: who pays what, and why.

Everything the figures, the page and the README state comes from the
story.json this writes, so they cannot drift apart.
"""

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# Speaker counts for the cost-weighted view, rough public figures (millions,
# first plus second language). Only used to say "billions of people", never
# for precise claims.
BIG_LANGUAGES = {
    "eng_Latn": ("English", 1500), "zho_Hans": ("Mandarin", 1100),
    "hin_Deva": ("Hindi", 600), "spa_Latn": ("Spanish", 550),
    "fra_Latn": ("French", 300), "arb_Arab": ("Arabic (MSA)", 270),
    "ben_Beng": ("Bengali", 270), "por_Latn": ("Portuguese", 260),
    "rus_Cyrl": ("Russian", 250), "urd_Arab": ("Urdu", 230),
    "ind_Latn": ("Indonesian", 200), "deu_Latn": ("German", 130),
    "jpn_Jpan": ("Japanese", 125), "swh_Latn": ("Swahili", 80),
    "yor_Latn": ("Yoruba", 45), "amh_Ethi": ("Amharic", 60),
    "hau_Latn": ("Hausa", 80), "ibo_Latn": ("Igbo", 30),
    "tam_Taml": ("Tamil", 85), "tel_Telu": ("Telugu", 95),
    "mya_Mymr": ("Burmese", 40), "khm_Khmr": ("Khmer", 18),
    "sin_Sinh": ("Sinhala", 17), "zul_Latn": ("Zulu", 27),
}

SCRIPT_NAMES = {
    "Latn": "Latin", "Cyrl": "Cyrillic", "Arab": "Arabic", "Deva": "Devanagari",
    "Ethi": "Ge'ez (Ethiopic)", "Beng": "Bengali", "Taml": "Tamil",
    "Telu": "Telugu", "Mymr": "Myanmar", "Khmr": "Khmer", "Sinh": "Sinhala",
    "Hans": "Han (simplified)", "Hant": "Han (traditional)", "Jpan": "Japanese",
    "Hang": "Hangul", "Grek": "Greek", "Hebr": "Hebrew", "Thai": "Thai",
    "Laoo": "Lao", "Geor": "Georgian", "Armn": "Armenian", "Tibt": "Tibetan",
    "Olck": "Ol Chiki", "Orya": "Odia", "Gujr": "Gujarati", "Guru": "Gurmukhi",
    "Knda": "Kannada", "Mlym": "Malayalam", "Tfng": "Tifinagh",
}


def build(measurements_path=None, out_path=None):
    m = json.loads(Path(measurements_path or
                        ROOT / "benchmarks" / "measurements.json").read_text())
    rows = m["rows"]

    by_tok = defaultdict(list)
    for r in rows:
        by_tok[r["tokenizer"]].append(r)

    # per-tokenizer equity stats over all languages
    tok_stats = {}
    for t, rs in by_tok.items():
        prem = np.array([r["premium"] for r in rs])
        tok_stats[t] = {
            "family": rs[0]["family"],
            "median_premium": float(np.median(prem)),
            "p90_premium": float(np.percentile(prem, 90)),
            "max_premium": float(prem.max()),
            "max_language": rs[int(prem.argmax())]["language"],
            "share_over_2x": float((prem > 2).mean()),
            "share_over_4x": float((prem > 4).mean()),
        }

    # per-language medians across the frontier tokenizers (the ones people pay for)
    frontier = ["gpt-3.5/4 (cl100k)", "gpt-4o (o200k)", "qwen2.5"]
    lang_prem = defaultdict(dict)
    for r in rows:
        lang_prem[r["language"]][r["tokenizer"]] = r["premium"]
    lang_frontier = {
        code: float(np.median([d[t] for t in frontier]))
        for code, d in lang_prem.items()
    }

    # script aggregation under GPT-4o's tokenizer
    script_rows = defaultdict(list)
    for code, d in lang_prem.items():
        script = code.split("_")[1]
        script_rows[script].append(d["gpt-4o (o200k)"])
    scripts = sorted(
        ({"script": s, "name": SCRIPT_NAMES.get(s, s),
          "n_languages": len(v), "median_premium": float(np.median(v))}
         for s, v in script_rows.items() if len(v) >= 2),
        key=lambda x: -x["median_premium"])

    lang_names = json.loads((ROOT / "assets" / "lang_names.json").read_text())
    ranked = sorted(lang_frontier.items(), key=lambda kv: -kv[1])
    named = [{"code": c,
              "name": BIG_LANGUAGES.get(c, (lang_names.get(c, c), None))[0],
              "speakers_m": BIG_LANGUAGES.get(c, (None, None))[1],
              "frontier_premium": p,
              "o200k": lang_prem[c]["gpt-4o (o200k)"],
              "nllb": lang_prem[c]["nllb"],
              "gpt2": lang_prem[c]["gpt2"]}
             for c, p in ranked]

    story = {
        "n_languages": m["n_languages"], "n_sentences": m["n_sentences"],
        "n_tokenizers": len(m["tokenizers"]),
        "tokenizer_stats": tok_stats,
        "languages_ranked": named,
        "big_languages": [x for x in named if x["code"] in BIG_LANGUAGES],
        "scripts_o200k": scripts,
        "diacritic_surcharge": m["diacritic_surcharge"],
        "worst_10_frontier": named[:10],
        "yoruba": next(x for x in named if x["code"] == "yor_Latn"),
        "amharic": next(x for x in named if x["code"] == "amh_Ethi"),
    }
    out = Path(out_path or ROOT / "assets" / "story.json")
    out.write_text(json.dumps(story, indent=1))

    # everything the explorer page needs, one small file
    tok_order = list(tok_stats)
    explorer = {
        "tokenizers": [{"name": t, "family": tok_stats[t]["family"],
                        "median": round(tok_stats[t]["median_premium"], 3)}
                       for t in tok_order],
        "surcharge": {t: round(m["diacritic_surcharge"][t]["surcharge"], 3)
                      for t in tok_order},
        "languages": [
            {"code": c, "name": x["name"], "script": c.split("_")[1],
             "speakers_m": x["speakers_m"],
             "premiums": [round(lang_prem[c][t], 3) for t in tok_order]}
            for c, x in ((y["code"], y) for y in named)],
    }
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "data.json").write_text(
        json.dumps(explorer, separators=(",", ":"), ensure_ascii=False))
    return story


if __name__ == "__main__":
    s = build()
    print(f"{s['n_languages']} languages x {s['n_tokenizers']} tokenizers")
    print("worst frontier premiums:")
    for x in s["worst_10_frontier"][:6]:
        print(f"  {x['code']:<10} {x['frontier_premium']:.2f}x")
    print(f"yoruba: frontier {s['yoruba']['frontier_premium']:.2f}x, "
          f"nllb {s['yoruba']['nllb']:.2f}x")
    ds = s["diacritic_surcharge"]["gpt-4o (o200k)"]
    print(f"diacritic surcharge (o200k): {ds['surcharge']:.3f}x")
