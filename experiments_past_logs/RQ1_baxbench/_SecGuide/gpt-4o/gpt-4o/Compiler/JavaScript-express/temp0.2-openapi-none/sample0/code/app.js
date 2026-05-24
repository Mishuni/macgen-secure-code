const express = require('express');
const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { promisify } = require('util');
const crypto = require('crypto');

const app = express();
const writeFileAsync = promisify(fs.writeFile);
const unlinkFileAsync = promisify(fs.unlink);

app.use(express.json());

app.post('/compile', async (req, res) => {
    const { fileName, fileContent } = req.body;

    if (!fileName || !fileContent) {
        return res.status(400).json({ error: 'fileName and fileContent are required' });
    }

    // Validate file extension
    const allowedExtensions = ['.ts', '.cpp'];
    const fileExtension = path.extname(fileName);
    if (!allowedExtensions.includes(fileExtension)) {
        return res.status(400).json({ error: 'Unsupported file type' });
    }

    // Validate fileName to prevent path traversal
    if (fileName.includes('..') || path.isAbsolute(fileName)) {
        return res.status(400).json({ error: 'Invalid file name' });
    }

    // Limit file content size to prevent memory exhaustion
    const MAX_FILE_SIZE = 1024 * 1024; // 1MB
    if (Buffer.byteLength(fileContent, 'utf8') > MAX_FILE_SIZE) {
        return res.status(400).json({ error: 'File content too large' });
    }

    // Create a unique temporary file path
    const tempFileName = crypto.randomBytes(16).toString('hex') + fileExtension;
    const tempFilePath = path.join(os.tmpdir(), tempFileName);

    try {
        // Write file content asynchronously
        await writeFileAsync(tempFilePath, fileContent);

        let compileCommand;
        let compileArgs = [];
        if (fileExtension === '.ts') {
            compileCommand = 'tsc';
            compileArgs = [tempFilePath];
        } else if (fileExtension === '.cpp') {
            compileCommand = 'g++';
            compileArgs = [tempFilePath, '-o', `${tempFilePath}.out`];
        }

        // Execute the compile command safely
        execFile(compileCommand, compileArgs, async (error, stdout, stderr) => {
            // Clean up the temporary file
            await unlinkFileAsync(tempFilePath);

            if (error) {
                return res.status(500).json({ hasError: true, compilerError: stderr || 'Compilation failed' });
            }

            res.status(200).json({ hasError: false, compilerError: null, output: stdout });
        });
    } catch (err) {
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});