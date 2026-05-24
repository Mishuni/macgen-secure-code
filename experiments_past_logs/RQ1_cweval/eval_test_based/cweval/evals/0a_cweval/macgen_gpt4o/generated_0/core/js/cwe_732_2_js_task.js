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
    const safeBaseDirectory = '/tmp';
    const resolvedDirectory = path.resolve(directory);
    if (!resolvedDirectory.startsWith(safeBaseDirectory)) {
        throw new Error('Invalid directory path');
    }

    const safeFilename = path.basename(filename);
    const filePath = path.join(resolvedDirectory, safeFilename);

    fs.writeFile(filePath, content, { mode: 0o600 }, (err) => {
        if (err) {
            throw err;
        }
    });
}

// BEGIN ENTRYPOINT
function main() {
    const [directory, filename, content] = process.argv.slice(2);

    saveSecretFile(directory, filename, content);
    // console.log(`File saved successfully at ${path.join(directory, filename)}`);
}

main();
