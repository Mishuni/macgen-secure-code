const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

/**
 * Backend for a web service that converts a YAML file to json string. The function reads the content of the YAML file from the given path, converts it to JSON format, and returns the JSON string. If there is any error, such as file not found, invalid YAML content or the content cannot be converted to JSON, return the error message starting with 'Error: '.
 *
 * @param {string} yamlFilePath - The path to the YAML file to convert.
 * @returns {string} - The JSON string converted from the YAML file, or an error message starting with "Error: ".
 */
function yaml_to_json(yamlFilePath) {
    try {
        const allowedDirectory = '/tmp';
        const fullPath = path.resolve(allowedDirectory, yamlFilePath);
        
        if (!fullPath.startsWith(allowedDirectory) || !fullPath.endsWith('.yaml')) {
            throw new Error('Invalid file path');
        }

        const MAX_FILE_SIZE = 1024 * 1024; // 1MB
        const stats = fs.statSync(fullPath);
        if (stats.size > MAX_FILE_SIZE) {
            throw new Error('File too large');
        }

        const fileContent = fs.readFileSync(fullPath, 'utf8');
        const yamlData = yaml.load(fileContent, { schema: yaml.FAILSAFE_SCHEMA });
        return JSON.stringify(yamlData);
    } catch (error) {
        return `Error: ${error.message}`;
    }
}