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
    // Allowlist of acceptable file extensions
    const allowedExtensions = ['.txt', '.md', '.json'];

    // Validate filename: stricter regex to prevent directory traversal and encoding tricks
    const validFilenameRegex = /^[a-zA-Z0-9 _-]+\.[a-zA-Z0-9]+$/;
    if (!validFilenameRegex.test(filename)) {
        return '';
    }

    // Validate file extension (case-insensitive)
    const fileExtension = path.extname(filename).toLowerCase();
    if (!allowedExtensions.includes(fileExtension)) {
        return '';
    }

    try {
        // Canonicalize the path to prevent directory traversal
        const safeDirPath = path.resolve(dir_path) + path.sep;
        const safeFilePath = path.resolve(safeDirPath, filename);

        // Ensure the file path is within the specified directory
        if (!safeFilePath.startsWith(safeDirPath)) {
            return '';
        }

        // Read the file content asynchronously
        return fs.readFileSync(safeFilePath, 'utf8');
    } catch (error) {
        // Return an empty string if any error occurs
        return '';
    }
}