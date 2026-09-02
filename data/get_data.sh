#!/usr/bin/env bash
# FLORES-200 devtest: 1,012 sentences professionally translated into 200+
# languages, the standard parallel benchmark (NLLB Team 2022, CC-BY-SA 4.0),
# from Meta's public distribution.
set -euo pipefail
cd "$(dirname "$0")"
curl -sL "https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz" -o flores200.tar.gz
tar xzf flores200.tar.gz
ls flores200_dataset/devtest | wc -l
