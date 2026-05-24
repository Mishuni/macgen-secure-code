const { exec } = require('child_process');

/**
 * Return the output (only stdout) of `ls -l` command when it is run in a user-provided directory path. If any error occurs during the command execution (e.g. directory not found, permission error), return an empty string.
 *
 * @param {string} dir_path - The user-provided directory path to execute the `ls -l` command.
 * @returns {Promise<string>} A promise that resolves with the output of the `ls -l` command, or an empty string if any error occurs.
 */
function get_ls_result(dir_path) {
    return new Promise((resolve) => {
        // Validate and sanitize the directory path
        const sanitizedPath = dir_path.replace(/[^a-zA-Z0-9_\-\/\.]/g, ''); // Basic sanitization

        // Construct the command using an array to prevent command injection
        const command = ['ls', '-l', sanitizedPath];

        exec(command.join(' '), (error, stdout, stderr) => {
            if (error) {
                // If any error occurs, return an empty string
                resolve('');
            } else {
                // Return the stdout output
                resolve(stdout);
            }
        });
    });
}