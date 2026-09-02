"""Contracts on the analysis layer: names resolve, payloads stay honest."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_every_language_has_a_real_name():
    names = json.loads((ROOT / "assets" / "lang_names.json").read_text())
    story = json.loads((ROOT / "assets" / "story.json").read_text())
    assert len(names) == story["n_languages"] == 204
    for x in story["languages_ranked"]:
        # a raw FLORES code leaking through means the name map has a hole
        assert x["name"] != x["code"], x["code"]


def test_mandarin_is_in_the_big_languages():
    # regression: FLORES-200 ships zho_Hans, not cmn_Hans; the first cut of
    # BIG_LANGUAGES used cmn and silently dropped 1.1 billion speakers
    story = json.loads((ROOT / "assets" / "story.json").read_text())
    big = {x["name"] for x in story["big_languages"]}
    assert "Mandarin" in big and len(big) == 24


def test_explorer_payload_matches_story():
    story = json.loads((ROOT / "assets" / "story.json").read_text())
    ex = json.loads((ROOT / "docs" / "data.json").read_text())
    assert len(ex["languages"]) == story["n_languages"]
    assert len(ex["tokenizers"]) == story["n_tokenizers"]
    toks = [t["name"] for t in ex["tokenizers"]]
    i = toks.index("gpt-4o (o200k)")
    yor = next(l for l in ex["languages"] if l["code"] == "yor_Latn")
    assert abs(yor["premiums"][i] - story["yoruba"]["o200k"]) < 5e-3
    eng = next(l for l in ex["languages"] if l["code"] == "eng_Latn")
    assert all(abs(p - 1.0) < 1e-9 for p in eng["premiums"])


if __name__ == "__main__":
    test_every_language_has_a_real_name()
    test_mandarin_is_in_the_big_languages()
    test_explorer_payload_matches_story()
    print("3 analyse contracts hold")
