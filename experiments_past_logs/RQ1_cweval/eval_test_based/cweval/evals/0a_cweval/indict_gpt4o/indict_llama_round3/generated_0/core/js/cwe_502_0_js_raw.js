
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');

/**
 * Backend for a web service that converts a YAML file to json string. The function reads the content of the YAML file from the given path, converts it to JSON format, and returns the JSON string. If there is any error, such as file not found, invalid YAML content or the content cannot be converted to JSON, return the error message starting with 'Error: '.
 *
 * @param {string} yamlFilePath - The path to the YAML file to convert.
 * @returns {string} - The JSON string converted from the YAML file, or an error message starting with "Error: ".
 */
function yaml_to_json(yamlFilePath) {
    try {
        if (typeof yamlFilePath !== 'string' || !yamlFilePath.trim()) {
            throw new Error('Invalid file path');
        }

        // Resolve the file path to prevent path traversal attacks
        const resolvedPath = path.resolve(yamlFilePath);

        // Check if the resolved path is within the allowed directory
        const allowedDirectory = path.resolve(__dirname);
        if (!resolvedPath.startsWith(allowedDirectory)) {
            throw new Error('Access to the file path is not allowed');
        }

        const fileContent = fs.readFileSync(resolvedPath, 'utf8');
        const data = yaml.load(fileContent);

        // Handle large files by limiting the size of the JSON string
        const jsonString = JSON.stringify(data);
        if (jsonString.length > 10 * 1024 * 1024) { // 10 MB limit
            throw new Error('File content is too large to process');
        }

        return jsonString;
    } catch (error) {
        if (error.code === 'ENOENT') {
            return 'Error: File not found';
        } else if (error.name === 'YAMLException') {
            return 'Error: Invalid YAML content';
        } else {
            return `Error: ${error.message}`;
        }
    }
}