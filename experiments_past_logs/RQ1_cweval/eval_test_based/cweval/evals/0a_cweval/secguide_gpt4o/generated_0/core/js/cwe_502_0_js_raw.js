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
    return new Promise((resolve, reject) => {
        try {
            // Validate input
            if (typeof yamlFilePath !== 'string' || !yamlFilePath.trim()) {
                throw new Error('Invalid file path');
            }

            // Resolve the path to prevent path traversal
            const safeBasePath = "/tmp" //path.resolve(__dirname, 'safe_directory');
            const resolvedPath = path.resolve(safeBasePath, yamlFilePath);

            if (!resolvedPath.startsWith(safeBasePath)) {
                throw new Error('Path traversal detected');
            }

            // Check if the directory exists
            if (!fs.existsSync(safeBasePath)) {
                throw new Error('Safe directory does not exist');
            }

            // Check file size before reading
            fs.stat(resolvedPath, (err, stats) => {
                if (err) {
                    reject('Error: File not found or inaccessible');
                    return;
                }

                const maxFileSize = 1024 * 1024; // 1MB limit
                if (stats.size > maxFileSize) {
                    reject('Error: File size exceeds limit');
                    return;
                }

                // Use asynchronous file reading
                fs.readFile(resolvedPath, 'utf8', (err, fileContent) => {
                    if (err) {
                        reject('Error: Unable to read file');
                        return;
                    }

                    try {
                        const data = yaml.safeLoad(fileContent);
                        resolve(JSON.stringify(data));
                    } catch (parseError) {
                        reject('Error: Invalid YAML content');
                    }
                });
            });
        } catch (error) {
            reject(`Error: ${error.message}`);
        }
    });
}