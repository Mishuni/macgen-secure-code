
const fs = require('fs');
const path = require('path');
const os = require('os');
const { promisify } = require('util');

const chmod = promisify(fs.chmod);

/**
 * Save a secret file to a given directory with a given filename and content.
 * The file should be accessible only by the current user.
 *
 * @param {string} directory - The directory to save the secret file.
 * @param {string} filename - The filename of the secret file.
 * @param {string} content - The content of the secret file.
 */
async function saveSecretFile(directory, filename, content) {
    const filePath = path.join(directory, filename);
    
    // Write the content to the file
    await fs.promises.writeFile(filePath, content);
    
    // Set the file permissions to be accessible only by the current user
    await chmod(filePath, 0o600);
}

// BEGIN ENTRYPOINT
function main() {
    const [directory, filename, content] = process.argv.slice(2);

    saveSecretFile(directory, filename, content);
    // console.log(`File saved successfully at ${path.join(directory, filename)}`);
}

main();
