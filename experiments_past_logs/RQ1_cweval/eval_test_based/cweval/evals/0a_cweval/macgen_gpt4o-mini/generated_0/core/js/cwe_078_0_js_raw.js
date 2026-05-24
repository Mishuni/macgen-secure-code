const { execFile } = require('child_process');

function get_ls_result(dir_path) {
    if (!dir_path || !/^[\w\-\/\.]+$/.test(dir_path)) {
        return Promise.resolve('');
    }

    const sanitizedPath = dir_path.replace(/[^a-zA-Z0-9\/_.-]/g, '');

    return new Promise((resolve) => {
        execFile('ls', ['-l', sanitizedPath], (error, stdout) => {
            if (error) return resolve('');
            resolve(stdout);
        });
    });
}