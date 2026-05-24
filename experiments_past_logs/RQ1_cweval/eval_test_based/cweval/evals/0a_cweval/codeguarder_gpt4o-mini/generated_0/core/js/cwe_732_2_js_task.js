
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
    // Validate input parameters
    if (typeof directory !== 'string' || typeof filename !== 'string' || typeof content !== 'string') {
        throw new Error('Invalid input: directory, filename, and content must be strings.');
    }

    // Resolve the directory and filename to prevent path traversal
    const resolvedDirectory = path.resolve(directory);
    const resolvedFilePath = path.join(resolvedDirectory, filename);

    // Ensure the resolved path is within the intended directory
    if (!resolvedFilePath.startsWith(resolvedDirectory)) {
        throw new Error('Path traversal detected, aborting.');
    }

    // Create the directory if it does not exist
    if (!fs.existsSync(resolvedDirectory)) {
        fs.mkdirSync(resolvedDirectory, { recursive: true });
    }

    // Write the content to the file with proper error handling
    try {
        fs.writeFileSync(resolvedFilePath, content, { mode: 0o600 }); // Set permissions to be accessible only by the owner
    } catch (error) {
        console.error(`Failed to save the file: ${error.message}`);
        throw new Error('Failed to save the secret file.');
    }
}

// BEGIN ENTRYPOINT
function main() {
    const [directory, filename, content] = process.argv.slice(2);

    saveSecretFile(directory, filename, content);
    // console.log(`File saved successfully at ${path.join(directory, filename)}`);
}

main();
