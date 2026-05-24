import json
import yaml
from yaml import SafeLoader, YAMLError
import os

def yaml_to_json(yaml_file_path: str) -> str:
    try:
        # Restrict file access to a specific directory
        allowed_directory = '/tmp/'
        if not yaml_file_path.startswith(allowed_directory):
            return 'Error: Unauthorized file access'

        # Prevent directory traversal
        if '..' in yaml_file_path or not os.path.isfile(yaml_file_path):
            return 'Error: Invalid file path'

        with open(yaml_file_path, 'r') as file:
            yaml_content = yaml.safe_load(file)
            json_content = json.dumps(yaml_content)
            return json_content
    except FileNotFoundError:
        return 'Error: File not found'
    except YAMLError:
        return 'Error: Invalid YAML content'
    except Exception:
        return 'Error: An unexpected error occurred'