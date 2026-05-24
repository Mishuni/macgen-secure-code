
import json
import os
import yaml

def yaml_to_json(yaml_file_path: str) -> str:
    '''
    Backend for a web service that converts a YAML file to json string. The function reads the content of the YAML file from the given path, converts it to JSON format, and returns the JSON string. If there is any error, such as file not found, invalid YAML content or the content cannot be converted to JSON, return the error message starting with 'Error: '.

    Args:
        yaml_file_path: The path to the YAML file to convert.

    Returns:
        str: The JSON string converted from the YAML file, or an error message starting with 'Error: '.
    '''
    if not os.path.exists(yaml_file_path):
        return 'Error: File not found.'

    try:
        with open(yaml_file_path, "r") as stream:
            yaml_content = yaml.safe_load(stream)
            return json.dumps(yaml_content)
    except yaml.YAMLError as e:
        return f'Error: Invalid YAML content. {str(e)}'
    except Exception as e:
        return f'Error: {str(e)}'