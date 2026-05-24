const express = require('express');
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

// Helper function to securely execute commands
function executeCommand(command, args, callback) {
    execFile(command, args, { timeout: 5000 }, (error, stdout, stderr) => {
        if (error) {
            callback(error, null, stderr);
        } else {
            callback(null, stdout, stderr);
        }
    });
}

// POST /compile endpoint
app.post('/compile', (req, res) => {
    const { fileName, fileContent } = req.body;

    // Validate input
    if (!fileName || !fileContent) {
        return res.status(400).json({ error: 'fileName and fileContent are required.' });
    }

    // Validate file extension
    const validExtensions = ['.ts', '.cpp'];
    const fileExtension = path.extname(fileName);
    if (!validExtensions.includes(fileExtension)) {
        return res.status(400).json({ error: 'Invalid file extension. Only .ts and .cpp are supported.' });
    }

    // Create a temporary directory for the file
    const tempDir = path.join(__dirname, 'temp');
    if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir);
    }

    // Write the file to the temporary directory
    const filePath = path.join(tempDir, fileName);
    fs.writeFileSync(filePath, fileContent);

    // Determine the compiler and arguments based on the file extension
    let compiler, args;
    if (fileExtension === '.ts') {
        compiler = 'tsc'; // TypeScript compiler
        args = [filePath];
    } else if (fileExtension === '.cpp') {
        compiler = 'g++'; // C++ compiler
        args = ['-o', path.join(tempDir, 'output'), filePath];
    }

    // Execute the compiler
    executeCommand(compiler, args, (error, stdout, stderr) => {
        // Clean up the temporary file
        fs.unlinkSync(filePath);

        if (error) {
            // Compilation failed
            return res.status(200).json({
                hasError: true,
                compilerError: stderr || 'Unknown compilation error.',
            });
        }

        // Compilation succeeded
        return res.status(200).json({
            hasError: false,
            compilerError: null,
        });
    });
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});