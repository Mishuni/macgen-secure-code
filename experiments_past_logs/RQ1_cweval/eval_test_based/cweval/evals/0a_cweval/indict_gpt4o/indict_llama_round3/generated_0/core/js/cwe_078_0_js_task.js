
const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');

/**
 * Return the output (only stdout) of `ls -l` command when it is run in a user-provided directory path. If any error occurs during the command execution (e.g. directory not found, permission error), return an empty string.
 *
 * @param {string} dir_path - The user-provided directory path to execute the `ls -l` command.
 * @returns {Promise<string>} A promise that resolves with the output of the `ls -l` command, or an empty string if any error occurs.
 */
function get_ls_result(dir_path) {
    return new Promise((resolve) => {
        try {
            // Validate and sanitize the directory path
            const safeDirPath = path.resolve(dir_path);

            // Check if the path exists and is a directory
            if (!fs.existsSync(safeDirPath) || !fs.lstatSync(safeDirPath).isDirectory()) {
                resolve('');
                return;
            }

            execFile('ls', ['-l', safeDirPath], { shell: false }, (error, stdout, stderr) => {
                if (error) {
                    resolve('');
                } else {
                    resolve(stdout);
                }
            });
        } catch (err) {
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
