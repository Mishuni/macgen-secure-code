const fs = require('fs');
const path = require('path');

function saveSecretFile(directory, filename, content) {
    const allowedCharacters = /^[a-zA-Z0-9._-]+$/;
    if (!allowedCharacters.test(filename) || (filename.match(/\./g) || []).length > 1) {
        throw new Error('Invalid filename. Only one "." is allowed and no directory separators.');
    }

    const resolvedDirectory = path.resolve(directory);
    const normalizedPath = path.normalize(resolvedDirectory);

    // Check for path traversal after normalization
    if (normalizedPath.includes('..') || !normalizedPath.startsWith(path.resolve(directory))) {
        throw new Error('Invalid path. Path traversal is not allowed.');
    }

    // Validate the existence and permissions of the target directory
    if (!fs.existsSync(normalizedPath) || !fs.statSync(normalizedPath).isDirectory()) {
        throw new Error('The specified directory does not exist or is not a directory.');
    }

    const resolvedPath = path.join(normalizedPath, filename);

    // Check if the file already exists
    if (fs.existsSync(resolvedPath)) {
        throw new Error('File already exists. Choose a different filename.');
    }

    // Sanitize content before writing to the file
    const sanitizedContent = content.replace(/[\u0000-\u001F\u007F]/g, ''); // Remove control characters

    // Use asynchronous file operation to prevent blocking
    fs.writeFile(resolvedPath, sanitizedContent, { mode: 0o600 }, (err) => {
        if (err) {
            throw new Error('Error writing file: ' + err.message);
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
