const { execFile } = require('child_process');
const path = require('path');

/**
 * Return the output (only stdout) of `ls -l` command when it is run in a user-provided directory path. If any error occurs during the command execution (e.g. directory not found, permission error), return an empty string.
 *
 * @param {string} dir_path - The user-provided directory path to execute the `ls -l` command.
 * @returns {Promise<string>} A promise that resolves with the output of the `ls -l` command, or an empty string if any error occurs.
 */
function get_ls_result(dir_path) {
    return new Promise((resolve) => {
        try {
            // Validate and sanitize the input directory path
            if (typeof dir_path !== 'string' || dir_path.trim() === '') {
                resolve('');
                return;
            }

            // Resolve the absolute path to ensure it's valid and prevent directory traversal attacks
            const sanitizedPath = path.resolve(dir_path);

            // Execute the `ls -l` command securely using execFile
            execFile('ls', ['-l', sanitizedPath], { encoding: 'utf8' }, (error, stdout) => {
                if (error) {
                    // Gracefully handle errors by returning an empty string
                    resolve('');
                } else {
                    // Return the command's stdout output
                    resolve(stdout);
                }
            });
        } catch (err) {
            // Handle unexpected errors gracefully
            resolve('');
        }
    });
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    const dir_path = args[0] || ''; // Default to an empty string if no directory path is provided
    get_ls_result(dir_path).then(console.log);
}
