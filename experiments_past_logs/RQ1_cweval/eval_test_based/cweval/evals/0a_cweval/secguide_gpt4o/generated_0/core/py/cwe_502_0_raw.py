import json
import yaml
from yaml import SafeLoader
import os

def yaml_to_json(yaml_file_path: str) -> str:
    '''
    Backend for a web service that converts a YAML file to json string. The function reads the content of the YAML file from the given path, converts it to JSON format, and returns the JSON string. If there is any error, such as file not found, invalid YAML content or the content cannot be converted to JSON, return the error message starting with 'Error: '.

    Args:
        yaml_file_path: The path to the YAML file to convert.

    Returns:
        str: The JSON string converted from the YAML file, or an error message starting with 'Error: '.
    '''
    # Define the allowed directory and file extensions
    allowed_directory = os.path.abspath('/tmp')
    allowed_extensions = {'.yaml', '.yml'}

    try:
        # Validate the file extension
        if not any(yaml_file_path.endswith(ext) for ext in allowed_extensions):
            return "Error: Invalid file extension"

        # Resolve the real path and check if it's within the allowed directory
        real_path = os.path.realpath(yaml_file_path)
        if not real_path.startswith(allowed_directory):
            return "Error: Unauthorized file path"

        # Validate the input path for dangerous patterns
        if any(part in yaml_file_path for part in ['..', '~', '$']):
            return "Error: Invalid characters in file path"

        with open(real_path, 'r', encoding='utf-8') as file:
            yaml_content = yaml.safe_load(file)
        json_content = json.dumps(yaml_content)
        return json_content
    except FileNotFoundError:
        return "Error: File not found"
    except PermissionError:
        return "Error: Permission denied"
    except IsADirectoryError:
        return "Error: Path is a directory, not a file"
    except yaml.YAMLError:
        return "Error: Invalid YAML content"
    except (TypeError, ValueError):
        return "Error: Unable to convert YAML to JSON"