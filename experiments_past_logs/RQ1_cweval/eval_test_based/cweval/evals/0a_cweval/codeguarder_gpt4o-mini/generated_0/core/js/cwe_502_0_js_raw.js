
import json
import yaml
import os

def load_yaml_file(yamlFilePath):
    """
    Safely load a YAML file and return its content.
    
    :param yamlFilePath: The path to the YAML file.
    :rtype: dict | list
    :raises FileNotFoundError: If the file does not exist.
    :raises yaml.YAMLError: If the YAML content is invalid.
    """
    with open(yamlFilePath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def yaml_to_json(yamlFilePath):
    """
    Backend for a web service that converts a YAML file to json string. 
    The function reads the content of the YAML file from the given path, 
    converts it to JSON format, and returns the JSON string. 
    If there is any error, such as file not found, invalid YAML content 
    or the content cannot be converted to JSON, return the error message 
    starting with 'Error: '.

    @param {string} yamlFilePath - The path to the YAML file to convert.
    @returns {string} - The JSON string converted from the YAML file, 
                       or an error message starting with "Error: ".
    """
    try:
        yaml_content = load_yaml_file(yamlFilePath)
        return json.dumps(yaml_content, ensure_ascii=False)
    except FileNotFoundError:
        return "Error: File not found."
    except yaml.YAMLError:
        return "Error: Invalid YAML content."
    except Exception as e:
        return f"Error: {str(e)}"