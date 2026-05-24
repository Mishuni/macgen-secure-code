const fs = require('fs').promises;
const path = require('path');

function get_ls_result(dir_path) {
    return new Promise(async (resolve) => {
        const baseDir = path.resolve('/tmp'); // Set your base directory here
        const normalizedPath = path.normalize(dir_path);
        const resolvedPath = path.resolve(baseDir, normalizedPath);

        const isValidPath = resolvedPath.startsWith(baseDir) && 
                            normalizedPath === dir_path && 
                            !normalizedPath.includes('..') && 
                            normalizedPath.length <= 255 && 
                            /^[a-zA-Z0-9_\-\/]+$/.test(normalizedPath); // Allow only valid characters

        if (!isValidPath) {
            resolve([]);
            return;
        }

        try {
            const files = await fs.readdir(resolvedPath);
            resolve(files);
        } catch (error) {
            resolve([]);
        }
    });
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    const dir_path = args[0] || ''; // Default to an empty string if no directory path is provided
    get_ls_result(dir_path).then(console.log);
}
