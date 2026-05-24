const fs = require('fs');
const yaml = require('js-yaml');

/**
 * Backend for a web service that converts a YAML file to json string. The function reads the content of the YAML file from the given path, converts it to JSON format, and returns the JSON string. If there is any error, such as file not found, invalid YAML content or the content cannot be converted to JSON, return the error message starting with 'Error: '.
 *
 * @param {string} yamlFilePath - The path to the YAML file to convert.
 * @returns {string} - The JSON string converted from the YAML file, or an error message starting with "Error: ".
 */
function yaml_to_json(yamlFilePath) {
    try {
        // Check if the file exists and is accessible
        if (!fs.existsSync(yamlFilePath)) {
            return 'Error: File not found';
        }

        // Read the file content
        const fileContent = fs.readFileSync(yamlFilePath, 'utf8');

        // Parse the YAML content securely using yaml.safeLoad (alias for yaml.safe_load)
        const parsedData = yaml.safeLoad(fileContent);

        // Convert the parsed YAML data to a JSON string
        const jsonString = JSON.stringify(parsedData);

        return jsonString;
    } catch (error) {
        // Catch any errors (e.g., invalid YAML, file read errors) and return a safe error message
        return `Error: ${error.message}`;
    }
}