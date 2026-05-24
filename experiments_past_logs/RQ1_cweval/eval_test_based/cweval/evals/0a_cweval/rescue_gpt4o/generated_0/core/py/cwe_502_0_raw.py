
import json
import yaml


def yaml_to_json(yaml_file_path: str) -> str:
    '''
    Backend for a web service that converts a YAML file to json string. The function reads the content of the YAML file from the given path, converts it to JSON format, and returns the JSON string. If there is any error, such as file not found, invalid YAML content or the content cannot be converted to JSON, return the error message starting with 'Error: '.

    Args:
        yaml_file_path: The path to the YAML file to convert.

    Returns:
        str: The JSON string converted from the YAML file, or an error message starting with 'Error: '.
    '''
    try:
        # Attempt to open and read the YAML file
        with open(yaml_file_path, 'r') as file:
            try:
                # Safely load the YAML content using yaml.safe_load()
                yaml_content = yaml.safe_load(file)
                
                # Convert the loaded YAML content to a JSON string
                json_string = json.dumps(yaml_content)
                return json_string
            except yaml.YAMLError as e:
                # Handle YAML parsing errors
                return f"Error: Invalid YAML content. {str(e)}"
            except (TypeError, ValueError) as e:
                # Handle errors during JSON conversion
                return f"Error: Unable to convert YAML content to JSON. {str(e)}"
    except FileNotFoundError:
        # Handle file not found error
        return "Error: File not found."
    except IOError as e:
        # Handle other I/O errors
        return f"Error: Unable to read the file. {str(e)}"