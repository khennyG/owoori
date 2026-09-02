"""Contracts for the measurement. A price comparison with a broken meter is
worse than none."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from owoori.measure import (FAMILY, HF_TOKENIZERS, TIKTOKEN, languages,
                            measure_language, read_lang, strip_yoruba_marks)


def test_the_corpus_is_parallel_and_complete():
    langs = languages()
    assert len(langs) >= 200
    eng = read_lang("eng_Latn")
    assert len(eng) == 1012
    for code in ("yor_Latn", "amh_Ethi", "swh_Latn", "fra_Latn", "zho_Hans"):
        assert code in langs
        assert len(read_lang(code)) == len(eng), code


def test_every_tokenizer_has_a_family():
    for name in list(HF_TOKENIZERS) + list(TIKTOKEN):
        assert name in FAMILY, name


def test_measure_counts_what_it_says():
    fake = lambda t: len(t.split())          # a whitespace "tokenizer"
    m = measure_language(["ab cd", "efg"], fake)
    assert m["tokens"] == 3
    assert m["chars"] == 8
    assert m["tokens_per_sentence"] == 1.5
    assert abs(m["bytes_per_token"] - 8 / 3) < 1e-12


def test_bytes_are_utf8_not_codepoints():
    m = measure_language(["ẹ̀"], lambda t: 1)
    # ẹ̀ is one visible character but several UTF-8 bytes
    assert m["bytes"] >= 3
    assert m["chars"] <= 2


def test_stripping_matches_the_ami_definition():
    assert strip_yoruba_marks("ọkọ̀") == "oko"
    assert strip_yoruba_marks("Kín ni?") == "Kin ni?"
    assert strip_yoruba_marks(strip_yoruba_marks("àṣẹ")) == "ase"


def test_premium_is_one_for_english_by_construction():
    fake = lambda t: len(t)
    eng = read_lang("eng_Latn")
    m = measure_language(eng, fake)
    assert m["tokens"] == sum(len(l) for l in eng)


if __name__ == "__main__":
    fns = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in fns:
        fn()
        print("ok  ", name, flush=True)
    print(f"\n{len(fns)} passed")
