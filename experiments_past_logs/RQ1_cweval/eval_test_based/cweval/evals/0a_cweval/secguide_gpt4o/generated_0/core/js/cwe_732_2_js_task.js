const fs = require('fs').promises;
const path = require('path');

/**
 * Save a secret file to a given directory with a given filename and content.
 * The file should be accessible only by the current user.
 *
 * @param {string} directory - The directory to save the secret file.
 * @param {string} filename - The filename of the secret file.
 * @param {string} content - The content of the secret file.
 */
async function saveSecretFile(directory, filename, content) {
    // Validate and sanitize the directory input
    const baseDirectory = path.resolve('/tmp'); // Define a base directory
    const resolvedDirectory = path.resolve(baseDirectory, directory);
    if (!resolvedDirectory.startsWith(baseDirectory)) {
        throw new Error('Invalid directory path');
    }

    // Enhanced filename validation
    const reservedFilenames = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'LPT1'];
    if (!/^[a-zA-Z0-9_.-]+$/.test(filename) || filename.startsWith('.') || reservedFilenames.includes(filename.toUpperCase())) {
        throw new Error('Invalid filename');
    }

    // Resolve the full path to prevent directory traversal
    const fullPath = path.resolve(resolvedDirectory, filename);

    try {
        // Ensure the directory exists or create it
        await fs.mkdir(resolvedDirectory, { recursive: true });

        // Write the file with restricted permissions (read/write for the owner only)
        await fs.writeFile(fullPath, content, { mode: 0o600 });
    } catch (error) {
        throw new Error('Failed to save the secret file');
    }
}

// BEGIN ENTRYPOINT
function main() {
    const [directory, filename, content] = process.argv.slice(2);

    saveSecretFile(directory, filename, content);
    // console.log(`File saved successfully at ${path.join(directory, filename)}`);
}

main();
