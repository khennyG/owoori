"""The measurement: what every tokenizer charges every language.

The design that makes the comparison fair: FLORES-200 is the same 1,012
sentences professionally translated into every language, so token counts are
directly comparable as prices for the same information. The premium for a
language under a tokenizer is

    premium = tokens(language) / tokens(English)

over the identical parallel content. A premium of 2.4 means a speaker of that
language pays 2.4 times as much per API call, waits behind 2.4 times the
latency, and fits 2.4 times less of their language into any context window,
for the same meaning.
"""

import json
import unicodedata
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parents[1] / "data" / "flores200_dataset"

# The tokenizers under study. Every one is openly downloadable; the two
# gated families (Llama, Gemma) are noted in the README as untested.
HF_TOKENIZERS = {
    "gpt2": "openai-community/gpt2",
    "bloom": "bigscience/bloom",
    "qwen2.5": "Qwen/Qwen2.5-7B",
    "nllb": "facebook/nllb-200-distilled-600M",
    "xlm-r": "FacebookAI/xlm-roberta-base",
    "mbert": "google-bert/bert-base-multilingual-cased",
    "aya": "CohereForAI/aya-101",
    "phi-3": "microsoft/Phi-3-mini-4k-instruct",
    "mistral": "mistralai/Mistral-7B-v0.3",
    "falcon": "tiiuae/falcon-7b",
}
TIKTOKEN = {
    "gpt-3.5/4 (cl100k)": "cl100k_base",
    "gpt-4o (o200k)": "o200k_base",
}

FAMILY = {
    "gpt2": "English-centric BPE", "phi-3": "English-centric BPE",
    "mistral": "English-centric BPE", "falcon": "English-centric BPE",
    "gpt-3.5/4 (cl100k)": "frontier BPE", "gpt-4o (o200k)": "frontier BPE",
    "qwen2.5": "frontier BPE",
    "bloom": "multilingual by design", "nllb": "multilingual by design",
    "xlm-r": "multilingual by design", "mbert": "multilingual by design",
    "aya": "multilingual by design",
}


def languages():
    files = sorted((DATA / "devtest").glob("*.devtest"))
    return [f.stem for f in files]


def read_lang(code):
    p = DATA / "devtest" / f"{code}.devtest"
    return p.read_text(encoding="utf-8").splitlines()


def load_tokenizers(verbose=True):
    """name -> callable(text) -> token count."""
    out = {}
    from tokenizers import Tokenizer
    from huggingface_hub import hf_hub_download
    for name, repo in HF_TOKENIZERS.items():
        path = hf_hub_download(repo, "tokenizer.json")
        tok = Tokenizer.from_file(path)
        out[name] = (lambda t, _tok=tok: len(_tok.encode(t).ids))
        if verbose:
            print(f"  loaded {name}")
    import tiktoken
    for name, enc_name in TIKTOKEN.items():
        enc = tiktoken.get_encoding(enc_name)
        out[name] = (lambda t, _e=enc: len(_e.encode(t)))
        if verbose:
            print(f"  loaded {name}")
    return out


MARKS = {"̀", "́", "̣"}


def strip_yoruba_marks(s):
    """Same definition as my ami project: tone and dot-below marks removed."""
    out = [c for c in unicodedata.normalize("NFD", s) if c not in MARKS]
    return unicodedata.normalize("NFC", "".join(out))


def measure_language(lines, count_fn):
    toks = sum(count_fn(line) for line in lines)
    chars = sum(len(line) for line in lines)
    bts = sum(len(line.encode("utf-8")) for line in lines)
    return {"tokens": toks, "chars": chars, "bytes": bts,
            "tokens_per_sentence": toks / len(lines),
            "bytes_per_token": bts / max(toks, 1)}


def run(out_path=None, verbose=True):
    langs = languages()
    toks = load_tokenizers(verbose=verbose)
    eng = read_lang("eng_Latn")

    rows = []
    eng_counts = {}
    for tname, fn in toks.items():
        eng_counts[tname] = measure_language(eng, fn)

    for i, code in enumerate(langs):
        lines = read_lang(code)
        for tname, fn in toks.items():
            m = measure_language(lines, fn)
            m.update({"language": code, "tokenizer": tname,
                      "family": FAMILY[tname],
                      "premium": m["tokens"] / eng_counts[tname]["tokens"]})
            rows.append(m)
        if verbose and (i + 1) % 25 == 0:
            print(f"  [{i+1}/{len(langs)}] {code}")

    # the diacritic surcharge: Yoruba written properly vs stripped
    yor = read_lang("yor_Latn")
    yor_stripped = [strip_yoruba_marks(l) for l in yor]
    surcharge = {}
    for tname, fn in toks.items():
        full = measure_language(yor, fn)["tokens"]
        bare = measure_language(yor_stripped, fn)["tokens"]
        surcharge[tname] = {"marked_tokens": full, "stripped_tokens": bare,
                            "surcharge": full / bare}

    result = {"rows": rows, "diacritic_surcharge": surcharge,
              "n_sentences": len(eng), "n_languages": len(langs),
              "tokenizers": list(toks)}
    if out_path:
        Path(out_path).write_text(json.dumps(result))
    return result
