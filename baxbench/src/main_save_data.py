import argparse
import pathlib
from typing import Any

import docker

from env import all_envs
from print import (
    tasks_and_results_to_table,
    tasks_and_results_to_table_averages,
    tasks_and_results_to_csv_averages
)
from scenarios import all_scenarios
from tasks import Task, TaskHandler
import json

_DEFAULT_SAVE_PATH = pathlib.Path(__file__).parent.parent / "results"


def main(args: Any) -> None:

    # ----- Preparation -----#
    envs = all_envs
    exclude_envs = args.exclude_envs if args.exclude_envs else []
    envs = [e for e in all_envs if e.id not in exclude_envs]
    if args.envs:
        envs = [e for e in all_envs if e.id in args.envs]
    envs = sorted(envs, key=lambda e: e.id)

    print(len(envs))
    # envs = [e for e in envs if e.language == "Python" and not e.is_multi_file]
    # print(len(envs))
    # print(envs[0])
    # envs = envs[-5:-4]
    # print(envs)
    # exit(1)

    if not envs:
        raise Exception(
            f"Got an empty/invalid list of envs, possible choices: {[e.id for e in all_envs]}",
        )

    exclude_scenarios = args.exclude_scenarios if args.exclude_scenarios else []
    scenarios = [e for e in all_scenarios if e.id not in exclude_scenarios]
    if args.scenarios:
        scenarios = [
            e
            for e in all_scenarios
            if e.id in args.scenarios and e.id not in exclude_scenarios
        ]
    scenarios = sorted(scenarios, key=lambda s: s.id)
    # print(scenarios)
    print("=============")
    # print(len(scenarios))
    # print(scenarios[0])
    # print(type(scenarios[0]))
    # scenarios = scenarios[:3]
    print(len(scenarios))
    # exit(1)
    if not scenarios:
        raise Exception(
            f"Got an empty/invalid list of scenarios, possible choices: {[s.id for s in all_scenarios]}",
        )
    if args.only_samples:
        samples = args.only_samples
    else:
        samples = list(range(args.n_samples))

    if args.ks:
        ks = args.ks
    else:
        ks = [1, 5]

    # tasks = sorted(
    #     [
    #         Task(
    #             env=env,
    #             scenario=scenario,
    #             model="gpt-4",
    #             temperature=args.temperature,
    #             spec_type=args.spec_type,
    #             safety_prompt=args.safety_prompt,
    #             reasoning_effort=args.reasoning_effort,
    #             openrouter=args.openrouter,
    #             vllm=args.vllm,
    #         )
    #         for env in envs
    #         for scenario in scenarios
    #         # for model in args.models
    #         if env.language == "Python" and env.framework.lower() == "fastapi" # and not env.is_multi_file
    #         # if env.language.lower() == "javascript" 
    #     ],
    #     key=lambda t: t.id,
    # )
    # # tasks = tasks[:10]
    # print(len(tasks))
    # print("=============")
    # print(tasks[224].generate_prompt())
    # exit(1)
    env_name = "fastapi"
    full_data = [
        {
            "prompt_id": idx,
            "cwe_identifier": [],
            "language": env.language,
            "file_suffix": env.extension,
            "task_id": scenario.id,
            "short_app_description": scenario.short_app_description,
            "api_spec": scenario.api_spec,
            "text_spec": scenario.text_spec,
            "scenario_instructions": scenario.scenario_instructions,
            "allowed_packages": env.allowed_packages,
            "framework": env.framework,
            "manifest_files": env.manifest_files,
            "needs_db": scenario.needs_db,
            "is_multi_file": env.is_multi_file,
            "env_instructions": env.env_instructions,
            "prompt": Task(
                env=env,
                scenario=scenario,
                model="gpt-4",
                temperature=args.temperature,
                spec_type=args.spec_type,
                safety_prompt=args.safety_prompt,
                reasoning_effort=args.reasoning_effort,
                openrouter=args.openrouter,
                vllm=args.vllm,
                
            ).generate_prompt(without_format_instruction=True)[0],
            "simple_prompt": Task(
                env=env,
                scenario=scenario,
                model="gpt-4",
                temperature=args.temperature,
                spec_type=args.spec_type,
                safety_prompt=args.safety_prompt,
                reasoning_effort=args.reasoning_effort,
                openrouter=args.openrouter,
                vllm=args.vllm,
               
            ).generate_prompt(without_format_instruction=True)[1],
            "sample_cases": scenario.samples_case if hasattr(scenario, 'samples_case') else None,
            # "format_instruction" : scenario.format_instruction,
            # "action_header"
        }
        for idx, (env, scenario) in enumerate(
            ((env, scenario) for env in envs for scenario in scenarios), start=0
        )
        # if env.language == "Python" and env.framework.lower() !="django".lower() #== env_name
        # if env.language == "JavaScript" and env.framework.lower() !="nest".lower() #== env_name
    ]
    # out_path = "baxbench.json"
    print(len(full_data))
    # out_path = f"../../data/baxbench_{env_name}.json"
    # out_path = f"../../data/baxbench_python.json"
    # out_path = f"../../data/baxbench_js.json"
    out_path = f"../../data/baxbench.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False, indent=2, default=str)

    print(f"Saved full_data to {out_path}")
    exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "--models", type=str, nargs="+", required=True, help="List of models"
    # )
    # parser.add_argument(
    #     "--mode",
    #     type=str,
    #     choices=[
    #         "generate",
    #         "test",
    #         "evaluate",
    #         "extract",
    #     ],
    #     required=True,
    #     help="Mode in which to run the code",
    # )
    parser.add_argument(
        "--temperature", type=float, default=0.2, help="Temperature for sampling"
    )
    parser.add_argument(
        "--n_samples",
        type=int,
        default=5, #1, #5,
        help="The number of samples to generate or test. Will index from 0.",
    )
    parser.add_argument(
        "--reasoning_effort",
        type=str,
        default="high",
        choices=["low", "medium", "high"],
        help="The reasoning effort to use for reasoning models.",
    )
    parser.add_argument(
        "--only_samples",
        type=int,
        nargs="+",
        default=None,
        help="If given, it will restrict operations to these sample indices.",
    )
    parser.add_argument(
        "--ks", type=int, nargs="+", default=None, help="List of k for pass@k score."
    )
    parser.add_argument(
        "--envs",
        type=str,
        default=None,
        nargs="+",
        help="List of environments (if empty, then all environments are used)",
    )
    parser.add_argument(
        "--exclude_envs",
        type=str,
        default=None,
        nargs="+",
        help="List of environments to exclude",
    )
    parser.add_argument(
        "--scenarios",
        type=str,
        default=None,
        nargs="+",
        help="List of scenarios (if empty, then all scenarios are used)",
    )
    parser.add_argument(
        "--exclude_scenarios",
        type=str,
        default=None,
        nargs="+",
        help="List of scenarios to exclude",
    )
    parser.add_argument(
        "--spec_type",
        choices=["openapi", "text"],
        default="openapi",
        type=str,
        help="The type of specifications to use.",
    )
    parser.add_argument(
        "--safety_prompt",
        choices=["none", "generic", "specific"],
        default="none",
        type=str,
        help="The type of additional safety cue to use.",
    )
    parser.add_argument(
        "--results_dir",
        type=pathlib.Path,
        default=_DEFAULT_SAVE_PATH,
        help="Directory to save the results",
    )
    parser.add_argument(
        "--max_concurrent_runs",
        type=int,
        default=None,
        help="Maximum number of concurrent runs",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout for each test run in seconds.",
    )
    parser.add_argument(
        "--num_ports",
        type=int,
        default=10000,
        help="Number of ports to use for docker containers",
    )
    parser.add_argument(
        "--min_port",
        type=int,
        default=12345,
        help="Minimum port number to use for docker containers",
    )
    parser.add_argument(
        "--max_retries",
        type=int,
        default=20,
        help="Maximum number of retries for backoff during generation",
    )
    parser.add_argument(
        "--base_delay",
        type=float,
        default=1.0,
        help="Base delay for backoff during generation",
    )
    parser.add_argument(
        "--max_delay",
        type=float,
        default=128.0,
        help="Maximum delay for backoff during generation",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force generation even if the file already exists",
    )
    parser.add_argument(
        "--skip_failed",
        action="store_true",
        help="Skip failed tasks and continue with the rest",
    )
    parser.add_argument(
        "--prune_docker",
        action="store_true",
        help="Prune docker containers after running tests",
    )
    parser.add_argument(
        "--openrouter",
        action="store_true",
        help="Route requests through OpenRouter",
    )
    parser.add_argument(
        "--vllm",
        action="store_true",
        help="Use VLLM for generation",
    )
    parser.add_argument(
        "--vllm_port",
        type=int,
        default=8000,
        help="Port for VLLM server",
    )
    main(parser.parse_args())
