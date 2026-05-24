
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
    try:
        # Validate the file path to prevent path traversal attacks
        if not yaml_file_path.endswith('.yaml') and not yaml_file_path.endswith('.yml'):
            return "Error: Invalid file extension"

        # Ensure the file path is within a designated directory
        base_directory = os.path.abspath(os.path.dirname(__file__))
        full_path = os.path.abspath(yaml_file_path)
        if not full_path.startswith(base_directory):
            return "Error: Invalid file path"

        with open(yaml_file_path, 'r') as file:
            yaml_content = yaml.safe_load(file)
        json_content = json.dumps(yaml_content)
        return json_content
    except FileNotFoundError:
        return "Error: File not found"
    except yaml.YAMLError as e:
        return f"Error: Invalid YAML content - {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"