const fs = require('fs');
const path = require('path');

/**
 * Reads the content of a file from a specified directory. If any error occurs during the file reading process (e.g., file not found, permission error), returns an empty string.
 *
 * @param {string} filename - The name of the file to read, requested by a user.
 * @param {string} dir_path - The directory path where the file is located.
 * @returns {string} The content of the file, or an empty string if any error occurs.
 */
function read_file_from_dir(filename, dir_path) {
    // Sanitize and validate the inputs
    const safeDirPath = path.resolve(dir_path);
    const safeFilePath = path.join(safeDirPath, filename);

    // Ensure the file is within the allowed directory
    if (!safeFilePath.startsWith(safeDirPath)) {
        return ''; // Prevent directory traversal
    }

    try {
        // Read the file content
        const content = fs.readFileSync(safeFilePath, 'utf8');
        return content;
    } catch (error) {
        // Handle errors gracefully
        return ''; // Return an empty string on error
    }
}