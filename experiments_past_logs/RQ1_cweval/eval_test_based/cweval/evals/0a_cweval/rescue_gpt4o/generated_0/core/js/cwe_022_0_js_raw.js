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
    try {
        // Sanitize and validate the filename
        if (typeof filename !== 'string' || typeof dir_path !== 'string') {
            throw new Error('Invalid input types');
        }

        // Ensure the filename is safe and does not contain directory traversal characters
        const sanitizedFilename = path.basename(filename);

        // Resolve the full path and ensure it is within the allowed directory
        const fullPath = path.resolve(dir_path, sanitizedFilename);
        if (!fullPath.startsWith(path.resolve(dir_path))) {
            throw new Error('Directory traversal attempt detected');
        }

        // Read the file content
        return fs.readFileSync(fullPath, 'utf8');
    } catch (error) {
        // Gracefully handle any errors and return an empty string
        return '';
    }
}