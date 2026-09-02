"""The full sweep: 204 languages x 12 tokenizers, then the analysis.

About 20 minutes on a 4-core 2014 CPU; the tokenizers are downloaded from the
Hub on first run (a few hundred MB, cached after that).
"""

from pathlib import Path

from owoori.measure import run
from owoori.analyse import build

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    out = ROOT / "benchmarks" / "measurements.json"
    run(out_path=out)
    print(f"wrote {out}")
    build()
    print("wrote assets/story.json and docs/data.json")
