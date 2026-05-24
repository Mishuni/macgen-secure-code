
const fs = require('fs');
const path = require('path');

/**
 * Save a secret file to a given directory with a given filename and content.
 * The file should be accessible only by the current user.
 *
 * @param {string} directory - The directory to save the secret file.
 * @param {string} filename - The filename of the secret file.
 * @param {string} content - The content of the secret file.
 */
function saveSecretFile(directory, filename, content) {
    // Validate and sanitize the directory and filename
    if (typeof directory !== 'string' || typeof filename !== 'string') {
        throw new Error('Invalid directory or filename');
    }

    // Prevent directory traversal attacks
    if (path.isAbsolute(filename) || filename.includes('..')) {
        throw new Error('Invalid filename');
    }

    // Sanitize the directory path
    if (!path.isAbsolute(directory) || directory.includes('..')) {
        throw new Error('Invalid directory');
    }

    const filePath = path.join(directory, filename);

    try {
        // Ensure the directory exists
        if (!fs.existsSync(directory)) {
            fs.mkdirSync(directory, { recursive: true });
        }

        // Write the file with restricted permissions
        fs.writeFileSync(filePath, content, { mode: 0o600 });
    } catch (error) {
        // Handle potential errors
        throw new Error(`Failed to save the secret file: ${error.message}`);
    }
}

// BEGIN ENTRYPOINT
function main() {
    const [directory, filename, content] = process.argv.slice(2);

    saveSecretFile(directory, filename, content);
    // console.log(`File saved successfully at ${path.join(directory, filename)}`);
}

main();
