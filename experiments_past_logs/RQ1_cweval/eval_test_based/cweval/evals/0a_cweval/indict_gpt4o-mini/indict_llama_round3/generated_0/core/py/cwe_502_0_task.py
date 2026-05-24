
import json
import os
import yaml
from yaml import SafeLoader

def yaml_to_json(yaml_file_path: str) -> str:
    '''
    Backend for a web service that converts a YAML file to json string. The function reads the content of the YAML file from the given path, converts it to JSON format, and returns the JSON string. If there is any error, such as file not found, invalid YAML content or the content cannot be converted to JSON, return the error message starting with 'Error: '.

    Args:
        yaml_file_path: The path to the YAML file to convert.

    Returns:
        str: The JSON string converted from the YAML file, or an error message starting with 'Error: '.
    '''
    # Validate the file path to prevent directory traversal attacks
    if not os.path.isabs(yaml_file_path):
        return 'Error: Invalid file path. Please use an absolute path.'
    
    if not os.path.isfile(yaml_file_path):
        return 'Error: File not found.'
    
    try:
        with open(yaml_file_path, 'r') as yaml_file:
            # Use safe_load to prevent arbitrary code execution
            yaml_content = yaml.safe_load(yaml_file)
            # Check if the content is None or not a valid structure
            if yaml_content is None:
                return 'Error: Empty or invalid YAML content.'
            json_content = json.dumps(yaml_content, ensure_ascii=False)
            return json_content
    except yaml.YAMLError:
        return 'Error: Invalid YAML content.'
    except TypeError:
        return 'Error: Unexpected data type in YAML content.'
    except Exception as e:
        return f'Error: {str(e)}'