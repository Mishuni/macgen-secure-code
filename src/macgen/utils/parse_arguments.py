import argparse

parser = argparse.ArgumentParser(description="Run generation process")

# Data configuration
parser.add_argument(
    "--task",
    type=str,
    default=None,
    choices={"cweval", "llmseceval", "humaneval", "baxbench"},
    help="Type of generation tasks to be run",
)
parser.add_argument(
    "--prev_trial",
    type=str,
    default=None,
    help="Path to the last generation iteration",
)

# Agent configuration
parser.add_argument(
    "--strategy",
    type=str,
    default="indict_llama",
    choices={"indict_llama", "indict_commandr"},
    help="Generation strategy",
)
parser.add_argument(
    "--model",
    type=str,
    default=None,
    help="Base model to initialize llm agents",
)

# Generation configuration
parser.add_argument(
    "--debug",
    action="store_true",
    help="Enable this to debug with a single sample",
)
parser.add_argument(
    "--override",
    action="store_true",
    help="Enable this to override past generation output",
)
parser.add_argument(
    "--suffix",
    type=str,
    default="",
    help="Suffix to output path",
)
parser.add_argument(
    "--init",
    action="store_true",
    help="Enable this to direct generation",
)
parser.add_argument(
    "--ours",
    action="store_true",
    help="Enable ours",
)

parser.add_argument(
    "--output_path",
    type=str,
    default=None,
    help="output path if the response path is not folmulated",
)
parser.add_argument(
    "--pj_name",
    type=str,
    default="",
    help="Project name for the output path",
)

parser.add_argument(
    "--eval_target",
    type=str,
    default="",
    choices=["", "cybersec", "codeql", "both"],
    help="Evaluation target: 'cybersec', 'codeql', or 'both'",
)
parser.add_argument(
    "--compile_only",
    action="store_true",
    help="Enable this to debug with a single sample",
)

parser.add_argument(
    "--eval_type",
    type=str,
    choices=["trained", "trained-new", "not-trained", "none"],
    default="none",
)

## for model config
parser.add_argument(
    "--temperature", type=float, default=None, help="Sampling temperature for generation"
)
parser.add_argument(
    "--n_samples", type=int, default=1, help="Number of samples to generate"
)

parser.add_argument(
    "-c",
    "--config",
    default="./configs/base.yaml",
    help="EngineConfig YAML file path (default: ./configs/base.yaml)",
)
parser.add_argument(
    "--cwe_limit", type=int, default=None, help="CWE limit for the experiment"
)
