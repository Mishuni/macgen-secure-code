
const { exec } = require('child_process');
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
        // Validate and sanitize the directory path
        if (typeof dir_path !== 'string' || dir_path.trim() === '') {
            return resolve('');
        }

        const sanitizedPath = path.resolve(dir_path);

        // Check if the directory exists and is accessible
        fs.access(sanitizedPath, fs.constants.R_OK, (err) => {
            if (err) {
                return resolve('');
            }

            // Execute the `ls -l` command safely
            exec(`ls -l ${sanitizedPath}`, { shell: '/bin/sh' }, (error, stdout, stderr) => {
                if (error || stderr) {
                    return resolve('');
                }
                resolve(stdout.trim());
            });
        });
    });
}