
const fs = require('fs').promises;
const yaml = require('js-yaml');
const path = require('path');

/**
 * Backend for a web service that converts a YAML file to json string. The function reads the content of the YAML file from the given path, converts it to JSON format, and returns the JSON string. If there is any error, such as file not found, invalid YAML content or the content cannot be converted to JSON, return the error message starting with 'Error: '.
 *
 * @param {string} yamlFilePath - The path to the YAML file to convert.
 * @returns {Promise<string>} - The JSON string converted from the YAML file, or an error message starting with "Error: ".
 */
async function yaml_to_json(yamlFilePath) {
    // Validate the file path to prevent path traversal attacks
    const normalizedPath = path.normalize(yamlFilePath);
    const baseDir = path.resolve(__dirname); // Adjust this to your base directory
    if (!normalizedPath.startsWith(baseDir)) {
        return 'Error: Invalid file path';
    }

    try {
        const fileContent = await fs.readFile(normalizedPath, 'utf8');
        
        // Use a safe loader to prevent DoS attacks
        const yamlData = yaml.load(fileContent, { schema: yaml.JSON_SCHEMA });
        
        return JSON.stringify(yamlData);
    } catch (error) {
        return `Error: ${error.message}`;
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
