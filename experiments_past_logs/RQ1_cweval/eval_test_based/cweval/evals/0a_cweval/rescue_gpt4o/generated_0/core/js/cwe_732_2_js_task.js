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
    try {
        // Validate and sanitize inputs
        if (typeof directory !== 'string' || typeof filename !== 'string' || typeof content !== 'string') {
            throw new Error('Invalid input types. All inputs must be strings.');
        }

        // Resolve absolute paths
        const safeBaseDir = path.resolve(directory);
        const safeFilePath = path.resolve(safeBaseDir, filename);

        // Ensure the file path is within the intended directory
        if (!safeFilePath.startsWith(safeBaseDir)) {
            throw new Error('Invalid file path. Directory traversal is not allowed.');
        }

        // Validate filename to prevent invalid or dangerous characters
        if (!/^[a-zA-Z0-9._-]+$/.test(filename)) {
            throw new Error('Invalid filename. Only alphanumeric characters, dots, underscores, and hyphens are allowed.');
        }

        // Ensure the directory exists
        if (!fs.existsSync(safeBaseDir)) {
            fs.mkdirSync(safeBaseDir, { recursive: true });
        }

        // Write the file with restricted permissions (read/write for the owner only)
        fs.writeFileSync(safeFilePath, content, { mode: 0o600 });

        console.log('File saved successfully.');
    } catch (error) {
        console.error(`Error saving file: ${error.message}`);
    }
}

// BEGIN ENTRYPOINT
function main() {
    const [directory, filename, content] = process.argv.slice(2);

    saveSecretFile(directory, filename, content);
    // console.log(`File saved successfully at ${path.join(directory, filename)}`);
}

main();
