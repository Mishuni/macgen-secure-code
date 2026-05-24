
import json
import yaml
import os

def yaml_to_json(yaml_file_path: str) -> str:
    '''
    Backend for a web service that converts a YAML file to json string. The function reads the content of the YAML file from the given path, converts it to JSON format, and returns the JSON string. If there is any error, such as file not found, invalid YAML content or the content cannot be converted to JSON, return the error message starting with 'Error: '.

    Args:
        yaml_file_path: The path to the YAML file to convert.

    Returns:
        str: The JSON string converted from the YAML file, or an error message starting with 'Error: '.
    '''
    if not os.path.isfile(yaml_file_path):
        return f"Error: File not found: {yaml_file_path}"

    try:
        with open(yaml_file_path, 'r', encoding='utf-8') as yaml_file:
            yaml_content = yaml_file.read()
            data = yaml.safe_load(yaml_content)  # Use safe_load to prevent arbitrary code execution
            json_string = json.dumps(data)  # Convert to JSON
            return json_string
    except yaml.YAMLError as e:
        return f"Error: Invalid YAML content: {str(e)}"
    except json.JSONDecodeError as e:
        return f"Error: Content cannot be converted to JSON: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"