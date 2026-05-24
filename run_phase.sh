#!/usr/bin/env bash
set -euo pipefail

# ===== Setup PYTHONPATH (include project root and src) =====
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${REPO_ROOT}:${REPO_ROOT}/src:${PYTHONPATH:-}"

# ===== Default values =====
MODEL=""   # Available: gpt4o-mini, deepseek-r1_70b, gemini-2.5-flash-lite, gemini-2.5-flash, qwen3_8b
TASK=""    # Task: llmseceval | cweval | humaneval | baxbench
BENCHMARK="instruct" # instruct | autocomplete

BASE_DIR="experiments"
PJ_NAME=""           # Project/experiment name (auto-generated if empty)
CWE_LIMIT="3"
INIT=false           # --init => run phase1; otherwise phase2
RUN_ALL=false        # --all  => run phase1 -> phase2 -> evaluate (phase2)
CONFIG_PATH="configs/base.yaml"
# ==================

usage() {
  cat <<'EOF'
Usage: ./run_phase.sh [options]

Options:
  --model <name>       (default: gpt4o-mini)
  --task <name>        (default: llmseceval) [cweval, llmseceval, humaneval, baxbench]
  --benchmark <name>   (default: instruct)
  --base-dir <path>    (default: experiments)
  --pj-name <name>     (no default; empty → TASK_MODEL_macgen)
  --cwe-limit <n>      (default: 3)
  --init               Run phase1 (initial generation) instead of phase2
  --all                Run phase1 then phase2, then evaluate on phase2 outputs
  --config <path>      (default: configs/base.yaml)
  -h, --help           Show this help message and exit

Examples:
  ./run_phase.sh --pj-name ph_1_test --cwe-limit 5 --init
  ./run_phase.sh --pj-name ph_2_test --config configs/custom.yaml
  ./run_phase.sh --task llmseceval --all
EOF
}

# ------- Parse command-line options -------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) MODEL="$2"; shift 2;;
    --task) TASK="$2"; shift 2;;
    --benchmark) BENCHMARK="$2"; shift 2;;
    --base-dir) BASE_DIR="$2"; shift 2;;
    --pj-name) PJ_NAME="$2"; shift 2;;
    --cwe-limit) CWE_LIMIT="$2"; shift 2;;
    --init) INIT=true; shift 1;;
    --all) RUN_ALL=true; shift 1;;
    --config) CONFIG_PATH="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unexpected option: $1"; usage; exit 1;;
  esac
done

# ------- Model Mapping (aliases) -------
case "$MODEL" in
  gemini-lite) MODEL="gemini-2.5-flash-lite" ;;
  gemini)      MODEL="gemini-2.5-flash" ;;
  deepseek)    MODEL="deepseek-r1_70b" ;;
esac

# ------- Baxbench API model name (actual name used by baxbench/src/main.py) -------
case "$MODEL" in
  gpt4o-mini)            BAXBENCH_MODEL="gpt-4o-mini" ;;
  gpt4o)                 BAXBENCH_MODEL="gpt-4o" ;;
  gpt4)                  BAXBENCH_MODEL="gpt-4.1" ;;
  gpt4-mini)             BAXBENCH_MODEL="gpt-4.1-mini" ;;
  gpt-o4-mini)           BAXBENCH_MODEL="o4-mini" ;;
  gemini-2.5-flash)      BAXBENCH_MODEL="gemini-2.5-flash" ;;
  gemini-2.5-flash-lite) BAXBENCH_MODEL="gemini-2.5-flash-lite" ;;
  deepseek-r1_70b)       BAXBENCH_MODEL="deepseek-r1:70b" ;;
  qwen3_8b)              BAXBENCH_MODEL="qwen3:8b" ;;
  qwen3_14b)             BAXBENCH_MODEL="qwen3:14b" ;;
  qwen3-coder_30b)       BAXBENCH_MODEL="qwen3-coder:30b" ;;
  *)                     BAXBENCH_MODEL="$MODEL" ;;
esac

# ------- Auto-generate PJ_NAME if empty -------
MODEL_SLUG="${MODEL//[^A-Za-z0-9._-]/-}"
if [[ -z "$PJ_NAME" ]]; then
  PJ_NAME="${TASK}_${MODEL_SLUG}_macgen"
fi

# ------- Define paths -------
EXP_DIR="${BASE_DIR}/${PJ_NAME}"
mkdir -p "$EXP_DIR"

# Phase1 condition: either --init OR --all
if [ "$INIT" = true ] || [ "$RUN_ALL" = true ]; then
  OUTPUT_PATH="${EXP_DIR}/_${MODEL_SLUG}_${TASK}_${CWE_LIMIT}.json"
  STAT_PATH="${EXP_DIR}/_stat_${CWE_LIMIT}_init.json"
  INIT_FLAG="--init"
else
  OUTPUT_PATH="${EXP_DIR}/_phase2_${MODEL_SLUG}_${TASK}_${CWE_LIMIT}.json"
  STAT_PATH="${EXP_DIR}/_stat_${CWE_LIMIT}.json"
  INIT_FLAG=""
fi


echo "=== Settings ==="
echo "MODEL       : $MODEL"
echo "TASK        : $TASK"
echo "BENCHMARK   : $BENCHMARK"
echo "BASE_DIR    : $BASE_DIR"
echo "PJ_NAME     : $PJ_NAME"
echo "CWE_LIMIT   : $CWE_LIMIT"
echo "OUTPUT_PATH : $OUTPUT_PATH"
echo "STAT_PATH   : $STAT_PATH"
echo "INIT        : $INIT"
echo "RUN_ALL     : $RUN_ALL"
echo

# ------- Run (single phase or ALL) -------
if [ "$RUN_ALL" = true ]; then
  echo "== [ALL] Phase1 =="
  python main.py \
    --pj_name "$PJ_NAME" \
    --model "$MODEL" \
    --config "$CONFIG_PATH" \
    --task "$TASK" \
    --cwe_limit "$CWE_LIMIT" \
    --init

  echo "== [ALL] Phase2 =="
  python main.py \
    --pj_name "$PJ_NAME" \
    --model "$MODEL" \
    --config "$CONFIG_PATH" \
    --task "$TASK" \
    --cwe_limit "$CWE_LIMIT"

  # Use phase2 outputs for evaluation
  OUTPUT_PATH="${EXP_DIR}/_phase2_${MODEL_SLUG}_${TASK}_${CWE_LIMIT}.json"
  STAT_PATH="${EXP_DIR}/_stat_${CWE_LIMIT}.json"
  INIT_FLAG=""

else
  # Single phase run
  python main.py \
    --pj_name "$PJ_NAME" \
    --model "$MODEL" \
    --config "$CONFIG_PATH" \
    --task "$TASK" \
    --cwe_limit "$CWE_LIMIT" ${INIT_FLAG:+$INIT_FLAG}
fi

# ------- Evaluation -------
if [[ "$TASK" == *cweval* ]]; then
  echo "== [CWEval] Export generated code =="
  python extract_res_for_cweval.py \
    --task cweval \
    --ours \
    --pj_name "$PJ_NAME" \
    --model "$MODEL" \
    --override \
    --cwe_limit "$CWE_LIMIT" ${INIT_FLAG:+$INIT_FLAG}

elif [[ "$TASK" == *humaneval* ]]; then
  JSONL_PATH="${OUTPUT_PATH%.json}.jsonl"
  echo "== [HumanEval] Functional correctness evaluation =="
  evalplus.evaluate \
    --dataset humaneval \
    --samples "$JSONL_PATH"
elif [[ "$TASK" == *llmseceval* ]]; then
  echo "== [LLMSecEval] Security benchmark =="
  python -m CybersecurityBenchmarks.benchmark.run \
    --benchmark="$BENCHMARK" \
    --use-precomputed-responses \
    --response-path="$OUTPUT_PATH" \
    --stat-path="$STAT_PATH"

  echo "== [CodeQL] Static vulnerability analysis =="
  python codeql_scan.py \
    --model "$MODEL" \
    --task "$TASK" \
    --output_path "$OUTPUT_PATH" \
    ${INIT_FLAG:+$INIT_FLAG}

elif [[ "$TASK" == *baxbench* ]]; then
  echo "== [BaxBench] Evaluation =="
  (
    cd "${REPO_ROOT}/baxbench/src"
    python main.py --n_samples 1 --model "$BAXBENCH_MODEL" \
      --results_dir "${REPO_ROOT}/${EXP_DIR}" --mode extract ${INIT_FLAG:+$INIT_FLAG}
    python main.py --n_samples 1 --model "$BAXBENCH_MODEL" \
      --results_dir "${REPO_ROOT}/${EXP_DIR}" --mode test ${INIT_FLAG:+$INIT_FLAG}
    python main.py --n_samples 1 --model "$BAXBENCH_MODEL" \
      --results_dir "${REPO_ROOT}/${EXP_DIR}" --mode evaluate ${INIT_FLAG:+$INIT_FLAG}
  )
fi
