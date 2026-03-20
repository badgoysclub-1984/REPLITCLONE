#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-$REPO_ROOT/datasets/raw}"

mkdir -p "$OUT_DIR"

download() {
  local url="$1"
  local name="$2"
  echo "Downloading $name..."
  curl -fsSL "$url" -o "$OUT_DIR/$name"
}

download "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv" "iris.csv"
download "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv" "penguins.csv"
download "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv" "titanic.csv"

echo "Done. Files written to: $OUT_DIR"
ls -lh "$OUT_DIR"
