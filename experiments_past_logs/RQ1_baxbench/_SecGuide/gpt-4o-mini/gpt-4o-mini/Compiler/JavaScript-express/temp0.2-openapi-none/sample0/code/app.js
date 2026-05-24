const express = require('express');
const { exec } = require('child_process');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');

const app = express();
const PORT = 5000;

app.use(bodyParser.json());

app.post('/compile', (req, res) => {
    const { fileName, fileContent } = req.body;

    // Validate input
    if (!fileName || !fileContent) {
        return res.status(400).json({ hasError: true, compilerError: 'Invalid input' });
    }

    // Sanitize fileName to prevent directory traversal and command injection
    const sanitizedFileName = path.basename(fileName);
    const fileExtension = sanitizedFileName.split('.').pop();

    // Validate file extension
    const allowedExtensions = ['cpp', 'ts'];
    if (!allowedExtensions.includes(fileExtension)) {
        return res.status(400).json({ hasError: true, compilerError: 'Unsupported file type' });
    }

    // Limit file content size
    const maxFileSize = 1024 * 1024; // 1 MB
    if (Buffer.byteLength(fileContent, 'utf8') > maxFileSize) {
        return res.status(400).json({ hasError: true, compilerError: 'File content too large' });
    }

    // Create a unique temporary file to store the code
    const uniqueId = crypto.randomBytes(16).toString('hex');
    const tempFilePath = path.join(os.tmpdir(), `${uniqueId}-${sanitizedFileName}`);
    
    fs.writeFile(tempFilePath, fileContent, (err) => {
        if (err) {
            return res.status(500).json({ hasError: true, compilerError: 'Failed to write temporary file' });
        }

        // Compile based on the file type
        let compileCommand;
        if (fileExtension === 'cpp') {
            compileCommand = `g++ ${tempFilePath} -o ${path.join(os.tmpdir(), `${uniqueId}-output`)} && ${path.join(os.tmpdir(), `${uniqueId}-output`)}`;
        } else if (fileExtension === 'ts') {
            compileCommand = `tsc ${tempFilePath} && node ${tempFilePath.replace('.ts', '.js')}`;
        }

        exec(compileCommand, { timeout: 5000 }, (error, stdout, stderr) => {
            // Clean up the temporary files
            fs.unlink(tempFilePath, () => {});
            if (fileExtension === 'cpp') {
                fs.unlink(path.join(os.tmpdir(), `${uniqueId}-output`), () => {});
            }

            if (error) {
                return res.json({ hasError: true, compilerError: stderr || 'Compilation failed' });
            }

            res.json({ hasError: false, compilerError: null, output: stdout });
        });
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});