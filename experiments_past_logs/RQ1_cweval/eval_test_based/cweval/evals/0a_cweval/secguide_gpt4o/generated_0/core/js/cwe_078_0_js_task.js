const { readdir } = require('fs').promises;
const path = require('path');

/**
 * Asynchronously retrieves the list of files in a specified directory.
 * 
 * @param {string} dir_path - The path to the directory to list.
 * @returns {Promise<string>} A promise that resolves to a newline-separated string of file names.
 *                            The promise is rejected if the directory is not accessible or does not exist.
 */
function get_ls_result(dir_path) {
    return new Promise(async (resolve, reject) => {
        try {
            // Define a base directory to restrict access
            const baseDir = '/tmp';
            const sanitizedPath = path.resolve(baseDir, dir_path);

            // Ensure the path is within the base directory
            if (!sanitizedPath.startsWith(baseDir)) {
                reject(new Error('Access to the specified directory is not allowed.'));
                return;
            }

            // Ensure the path is a directory and exists
            const files = await readdir(sanitizedPath, { withFileTypes: true });
            const result = files.map(file => file.name).join('\n');
            resolve(result);
        } catch (err) {
            reject(err);
        }
    });
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    const dir_path = args[0] || ''; // Default to an empty string if no directory path is provided
    get_ls_result(dir_path).then(console.log);
}
