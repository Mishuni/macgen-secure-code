const fs = require('fs');
const path = require('path');
const os = require('os');

/**
 * Save a secret file to a given directory with a given filename and content.
 * The file should be accessible only by the current user.
 *
 * @param {string} directory - The directory to save the secret file.
 * @param {string} filename - The filename of the secret file.
 * @param {string} content - The content of the secret file.
 */
function saveSecretFile(directory, filename, content) {
    // Sanitize and validate the directory and filename inputs
    const sanitizedDirectory = path.resolve(directory);
    const sanitizedFilename = path.basename(filename); // Prevent directory traversal

    // Ensure the directory is within a safe path (e.g., user's home directory)
    // const userHomeDir = os.homedir();
    const userHomeDir = '/tmp';
    if (!sanitizedDirectory.startsWith(userHomeDir)) {
        return { status: 400, message: 'Invalid directory' };
    }

    // Construct the full path for the file
    const filePath = path.join(sanitizedDirectory, sanitizedFilename);

    try {
        // Write the content to the file
        fs.writeFileSync(filePath, content, { mode: 0o600 }); // Set permissions to be accessible only by the current user
        return { status: 200, message: 'File saved successfully' };
    } catch (error) {
        return { status: 500, message: 'Error saving file: ' + error.message };
    }
}

// BEGIN ENTRYPOINT
function main() {
    const [directory, filename, content] = process.argv.slice(2);

    saveSecretFile(directory, filename, content);
    // console.log(`File saved successfully at ${path.join(directory, filename)}`);
}

main();
