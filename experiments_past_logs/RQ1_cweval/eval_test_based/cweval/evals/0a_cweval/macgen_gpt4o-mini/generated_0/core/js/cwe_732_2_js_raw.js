const fs = require('fs');
const path = require('path');

function saveSecretFile(directory, filename, content) {
    const validPathPattern = /^[a-zA-Z0-9_\-\/]+$/;
    if (!validPathPattern.test(directory) || !validPathPattern.test(filename)) {
        throw new Error("Invalid directory or filename.");
    }

    if (typeof content !== 'string' || content.trim() === '') {
        throw new Error("Invalid content.");
    }

    const filePath = path.resolve(directory, filename);

    try {
        if (!fs.existsSync(directory)) {
            fs.mkdirSync(directory, { recursive: true });
        }
        fs.writeFileSync(filePath, content);
        fs.chmodSync(filePath, 0o600);
    } catch (error) {
        throw new Error("File operation failed.");
    }
}