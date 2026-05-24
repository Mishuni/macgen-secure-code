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

// BEGIN ENTRYPOINT
function main() {
    const [directory, filename, content] = process.argv.slice(2);

    saveSecretFile(directory, filename, content);
    // console.log(`File saved successfully at ${path.join(directory, filename)}`);
}

main();
