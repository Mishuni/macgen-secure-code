
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
    // Ensure the directory exists
    if (!fs.existsSync(directory)) {
        fs.mkdirSync(directory, { recursive: true, mode: 0o700 });
    }

    // Construct the full path securely
    const filePath = path.join(directory, path.basename(filename));

    // Write the file securely, ensuring it does not already exist
    try {
        fs.writeFileSync(filePath, content, { flag: 'wx', mode: 0o600 });
    } catch (err) {
        if (err.code !== 'EEXIST') throw err;
    }
}