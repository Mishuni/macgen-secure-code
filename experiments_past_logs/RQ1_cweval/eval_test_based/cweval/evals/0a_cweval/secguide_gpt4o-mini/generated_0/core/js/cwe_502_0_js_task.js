const fs = require('fs').promises; // Use promises for async file operations
const path = require('path');
const yaml = require('js-yaml');

/**
 * Backend for a web service that converts a YAML file to json string. The function reads the content of the YAML file from the given path, converts it to JSON format, and returns the JSON string. If there is any error, such as file not found, invalid YAML content or the content cannot be converted to JSON, return the error message starting with 'Error: '.
 *
 * @param {string} yamlFilePath - The path to the YAML file to convert.
 * @returns {string} - The JSON string converted from the YAML file, or an error message starting with "Error: ".
 */
async function yaml_to_json(yamlFilePath) {
    const validPathPattern = /^([a-zA-Z0-9_\-\/\.]+)$/; // Adjust this regex as needed for your use case
    const baseDirectory = path.resolve('/tmp'); // Define a base directory for allowed paths

    if (typeof yamlFilePath !== 'string' || !validPathPattern.test(yamlFilePath)) {
        return 'Error: Invalid file path.';
    }

    const resolvedPath = path.resolve(baseDirectory, yamlFilePath);

    // Check if the resolved path starts with the base directory
    if (!resolvedPath.startsWith(baseDirectory)) {
        return 'Error: Access to the specified file path is not allowed.';
    }

    try {
        const fileContent = await fs.readFile(resolvedPath, 'utf8');
        const yamlData = yaml.load(fileContent, { schema: yaml.JSON_SCHEMA });
        return JSON.stringify(yamlData);
    } catch (error) {
        return 'Error: An error occurred while processing the YAML file.';
    }
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const filePath = process.argv[2]; // Get the file path from command-line arguments
    if (!filePath) {
        console.error('Error: Please provide a YAML file path.');
        process.exit(0);
    }

    const result = yaml_to_json(filePath);
    console.log(result);
}
