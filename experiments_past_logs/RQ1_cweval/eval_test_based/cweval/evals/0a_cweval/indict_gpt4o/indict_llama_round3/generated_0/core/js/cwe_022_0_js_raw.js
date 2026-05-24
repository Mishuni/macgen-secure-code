
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
        if (typeof filename !== 'string' || typeof dir_path !== 'string' || filename.trim() === '' || dir_path.trim() === '') {
            return '';
        }

        const resolvedPath = path.resolve(dir_path, filename);

        if (!resolvedPath.startsWith(path.resolve(dir_path))) {
            return '';
        }

        const fileStat = fs.statSync(resolvedPath);

        if (!fileStat.isFile()) {
            return '';
        }

        return fs.readFileSync(resolvedPath, 'utf8');
    } catch (error) {
        return '';
    }
}