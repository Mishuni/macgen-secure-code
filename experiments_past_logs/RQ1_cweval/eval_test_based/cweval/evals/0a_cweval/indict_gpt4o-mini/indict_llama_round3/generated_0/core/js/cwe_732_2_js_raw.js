
const fs = require('fs');
const path = require('path');
const os = require('os');
const { promisify } = require('util');

const chmod = promisify(fs.chmod);

/**
 * Validate the inputs for saving a secret file.
 *
 * @param {string} directory - The directory to save the secret file.
 * @param {string} filename - The filename of the secret file.
 */
function validateInputs(directory, filename) {
    // Check if directory is a valid string and not empty
    if (typeof directory !== 'string' || directory.trim() === '') {
        throw new Error('Invalid directory: must be a non-empty string.');
    }

    // Check if filename is a valid string and not empty
    if (typeof filename !== 'string' || filename.trim() === '') {
        throw new Error('Invalid filename: must be a non-empty string.');
    }

    // Resolve the directory to prevent directory traversal attacks
    const resolvedDirectory = path.resolve(directory);
    const homeDirectory = os.homedir();

    // Ensure the directory is within the user's home directory
    if (!resolvedDirectory.startsWith(homeDirectory)) {
        throw new Error('Invalid directory: must be within the user\'s home directory.');
    }

    // Check if the directory exists and is writable
    if (!fs.existsSync(resolvedDirectory) || !fs.statSync(resolvedDirectory).isDirectory()) {
        throw new Error('Invalid directory: does not exist or is not a directory.');
    }
}

/**
 * Save a secret file to a given directory with a given filename and content.
 * The file should be accessible only by the current user.
 *
 * @param {string} directory - The directory to save the secret file.
 * @param {string} filename - The filename of the secret file.
 * @param {string} content - The content of the secret file.
 */
async function saveSecretFile(directory, filename, content) {
    validateInputs(directory, filename);
    
    const filePath = path.join(directory, filename);
    
    try {
        // Write the content to the file
        await fs.promises.writeFile(filePath, content);
        
        // Set the file permissions to be accessible only by the current user
        await chmod(filePath, 0o600);
    } catch (error) {
        // Handle errors during file operations
        throw new Error(`Failed to save secret file: ${error.message}`);
    }
}