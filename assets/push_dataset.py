"""Publish the sweep to the Hub as a dataset: kenny0bi/tokenizer-tax.

The card's numbers are read from story.json, the same file the figures and
the page read, so nothing on the Hub can drift from what was measured.
"""

import csv
import io
import json
from pathlib import Path

from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parents[1]
REPO = "kenny0bi/tokenizer-tax"


def tidy_csv(measurements):
    buf = io.StringIO()
    cols = ["language", "tokenizer", "family", "premium", "tokens",
            "tokens_per_sentence", "chars", "bytes", "bytes_per_token"]
    w = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for r in measurements["rows"]:
        r = dict(r, premium=round(r["premium"], 4),
                 tokens_per_sentence=round(r["tokens_per_sentence"], 2),
                 bytes_per_token=round(r["bytes_per_token"], 3))
        w.writerow(r)
    return buf.getvalue()


def card(story):
    y, a = story["yoruba"], story["amharic"]
    worst = story["worst_10_frontier"][0]
    return f"""---
license: cc-by-sa-4.0
language: multilingual
task_categories: []
tags:
  - tokenization
  - fairness
  - multilinguality
  - flores-200
pretty_name: "owóorí: the tokenizer tax across 204 languages"
---

# owóorí: the tokenizer tax, measured

Token-count premiums for the 204 languages of FLORES-200 under 12
tokenizers, from the identical 1,012 professionally translated sentences.
The premium is `tokens(language) / tokens(English)` on the same content, so
it reads directly as a price multiplier for API cost, latency and context
shrinkage.

- **Interactive explorer:** https://kenny0bi.github.io/owoori/
- **Method, figures, code:** https://github.com/Kenny0bi/owoori

## Files

- `premiums.csv`: one row per language x tokenizer
  ({story['n_languages']} x {story['n_tokenizers']} = \
{story['n_languages'] * story['n_tokenizers']} rows): premium, raw token
  counts, characters, bytes, bytes per token.
- `measurements.json`: everything above plus the Yoruba diacritic-surcharge
  measurements (marked vs stripped text under every tokenizer).

## Headlines

- {worst['name']} pays **{worst['frontier_premium']:.2f}x** English's rate at
  the frontier (median of cl100k, o200k, Qwen2.5), the worst of the 204.
- 61% of languages pay more than 2x at the frontier; 17% pay more than 4x.
- The tax is a design choice: Amharic pays {a['o200k']:.2f}x under GPT-4o and
  {a['nllb']:.2f}x under NLLB; Yoruba pays {y['o200k']:.2f}x and
  {y['nllb']:.2f}x.
- Writing Yoruba with its tone and dot-below marks costs
  {story['diacritic_surcharge']['gpt-4o (o200k)']['surcharge']:.2f}x the
  stripped text under GPT-4o: a second tax, on orthography itself.

## Provenance

Source text: FLORES-200 devtest (NLLB Team 2022, CC-BY-SA 4.0), from Meta's
public distribution. Tokenizers: GPT-2, Phi-3, Mistral v0.3, Falcon-7B,
cl100k_base, o200k_base, Qwen2.5, NLLB-200, XLM-R, mBERT, Aya-101, BLOOM,
all loaded from their public repositories. Llama and Gemma are gated and not
included. Measurement code and tests are in the GitHub repository.
"""


if __name__ == "__main__":
    m = json.loads((ROOT / "benchmarks" / "measurements.json").read_text())
    story = json.loads((ROOT / "assets" / "story.json").read_text())
    api = HfApi()
    api.create_repo(REPO, repo_type="dataset", exist_ok=True)
    api.upload_file(path_or_fileobj=tidy_csv(m).encode(),
                    path_in_repo="premiums.csv", repo_id=REPO,
                    repo_type="dataset")
    api.upload_file(path_or_fileobj=ROOT / "benchmarks" / "measurements.json",
                    path_in_repo="measurements.json", repo_id=REPO,
                    repo_type="dataset")
    api.upload_file(path_or_fileobj=card(story).encode(),
                    path_in_repo="README.md", repo_id=REPO,
                    repo_type="dataset")
    print(f"published https://huggingface.co/datasets/{REPO}")
