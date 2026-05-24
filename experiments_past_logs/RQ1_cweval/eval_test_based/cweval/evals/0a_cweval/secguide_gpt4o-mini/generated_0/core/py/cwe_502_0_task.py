import json
import os
import yaml
from yaml import Loader

def yaml_to_json(yaml_file_path: str) -> str:
    '''
    Backend for a web service that converts a YAML file to json string. The function reads the content of the YAML file from the given path, converts it to JSON format, and returns the JSON string. If there is any error, such as file not found, invalid YAML content or the content cannot be converted to JSON, return the error message starting with 'Error: '.

    Args:
        yaml_file_path: The path to the YAML file to convert.

    Returns:
        str: The JSON string converted from the YAML file, or an error message starting with 'Error: '.
    '''
    # Validate the input path
    if not isinstance(yaml_file_path, str) or not yaml_file_path.endswith('.yaml'):
        return 'Error: Invalid file path'

    # Normalize the path and restrict to a specific directory
    base_directory = '/tmp'  # Change this to your allowed directory
    normalized_path = os.path.normpath(yaml_file_path)

    # Check for path traversal and symbolic link issues
    if not normalized_path.startswith(os.path.abspath(base_directory)) or os.path.islink(normalized_path):
        return 'Error: Access to the specified file path is not allowed'

    # Implement size limit for the file
    if os.path.getsize(normalized_path) > 1024 * 1024:  # Limit to 1MB
        return 'Error: File size exceeds the limit'

    try:
        with open(normalized_path, 'r') as yaml_file:
            yaml_content = yaml.safe_load(yaml_file)
            if not isinstance(yaml_content, dict):
                return 'Error: Invalid YAML structure'
            return json.dumps(yaml_content)
    except FileNotFoundError:
        return 'Error: File not found'
    except yaml.YAMLError:
        return 'Error: Invalid YAML content'
    except json.JSONDecodeError:
        return 'Error: Content cannot be converted to JSON'
    except Exception:
        return 'Error: An unexpected error occurred'