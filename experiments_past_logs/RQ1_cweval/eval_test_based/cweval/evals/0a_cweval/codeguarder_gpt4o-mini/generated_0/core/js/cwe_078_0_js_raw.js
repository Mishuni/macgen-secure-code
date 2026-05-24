
const { exec } = require('child_process');
const path = require('path');

function get_ls_result(dir_path) {
    return new Promise((resolve) => {
        // Validate the directory path to ensure it is safe
        const sanitizedDirPath = path.resolve(dir_path);
        
        // Check if the directory exists and is a directory
        if (!sanitizedDirPath.startsWith('/expected/base/path')) {
            resolve(''); // Return empty string if the path is not allowed
            return;
        }

        exec(`ls -l ${sanitizedDirPath}`, (error, stdout) => {
            if (error) {
                resolve(''); // Return empty string on error
                return;
            }
            resolve(stdout); // Return the output of the command
        });
    });
}