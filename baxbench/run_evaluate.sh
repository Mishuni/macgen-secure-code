#!/usr/bin/env bash
set -euo pipefail

#
# Usage:
#   ./run_exp.sh              → models=gpt-4o (default)
#   ./run_exp.sh gpt4omini    → models=gpt-4o-mini
#   ./run_exp.sh gpt4o-mini   → models=gpt-4o-mini
#   ./run_exp.sh gpt4o        → models=gpt-4o
#   ./run_exp.sh gemini-2.5-flash 
#

raw_model="${1:-gpt-4o}"

normalize_model() {
  local m="$1"
  local lower="${m,,}"          

  if [[ "$lower" =~ gpt4o || "$lower" =~ gpt-4o ]]; then
    if [[ "$lower" == *mini* ]]; then
      echo "gpt-4o-mini"
    else
      echo "gpt-4o"
    fi
  else
    echo "$raw_model"
  fi
}

MODEL="$(normalize_model "$raw_model")"

echo ">> Using model: ${MODEL}"
echo

# === Paths ===
BASE_DIR="$(pwd)"
EXP_DIR="${BASE_DIR}/../experiments/${MODEL}"

if [ ! -d "$EXP_DIR" ]; then
  echo "Error: experiments directory not found at: $EXP_DIR"
  exit 1
fi

# === Loop ===
for dir in "$EXP_DIR"/*/; do
  dir_name="$(basename "$dir")"
  echo "== Checking directory: $dir_name =="

  shopt -s nullglob
  json_files=("$dir"*.json)
  shopt -u nullglob

  if ((${#json_files[@]} == 0)); then
    echo "  -> Skipping (no JSON files)"
    continue
  fi

  has_bax_or_resp=false
  for f in "${json_files[@]}"; do
    base="$(basename "$f")"
    if [[ "$base" == *baxbench* || "$base" == *response* ]]; then
      has_bax_or_resp=true
      break
    fi
  done

  if ! $has_bax_or_resp; then
    echo "  -> Skipping (no baxbench/response JSON file)"
    continue
  fi

  results_dir="$dir"
  echo "  -> Running commands with results_dir=$results_dir"

  python src/main.py --models "$MODEL" --mode extract   --n_samples 1 --temperature 0.0 --results_dir "$results_dir" -f &
  python src/main.py --models "$MODEL" --mode test      --n_samples 1 --temperature 0.0 --results_dir "$results_dir" -f &
  python src/main.py --models "$MODEL" --mode evaluate  --n_samples 1 --temperature 0.0 --results_dir "$results_dir"  

  echo
done
