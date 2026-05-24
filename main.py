
from __future__ import annotations
import logging
import time, re
from pathlib import Path 
import sys
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from src.macgen.utils.parse_arguments import parser
from src.macgen.config import EngineConfig
from src.macgen.pipeline import MacgenEngine
# from src.macgen.pipeline_shared import MacgenEngine

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

if __name__ == "__main__":
    args = parser.parse_args()
    cfg = EngineConfig.from_yaml(args.config)

    # Only override config with values explicitly passed via CLI
    _CLI_TO_CFG = {
        "task": "task",
        "model": "model_name",
        "temperature": "temperature",
        "cwe_limit": "max_cwe_limit",
    }
    for cli_key, cfg_key in _CLI_TO_CFG.items():
        cli_val = getattr(args, cli_key, None)
        if cli_val is not None:
            setattr(cfg, cfg_key, cli_val)

    if not args.pj_name:
        model_slug = re.sub(r'[^A-Za-z0-9._-]+', '-', cfg.model_name)
        args.pj_name = f"/{model_slug}/{cfg.task}_{model_slug}_macgen"
    engine = MacgenEngine(cfg, out_dir=Path(f"./experiments/{args.pj_name}"))
    start_time = time.time()
    if args.init:
        engine.run_phase1()
    else:
        engine.run_phase2()
    logging.info("\nTotal time: %.2f minutes\n", (time.time() - start_time) / 60)
