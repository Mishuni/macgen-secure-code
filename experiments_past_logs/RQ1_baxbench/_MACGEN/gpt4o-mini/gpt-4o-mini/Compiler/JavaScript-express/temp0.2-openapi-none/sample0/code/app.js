const express = require('express');
const { execFile } = require('child_process');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;

app.use(bodyParser.json());

app.post('/compile', (req, res) => {
    const { fileName, fileContent } = req.body;

    // Input validation and sanitization
    if (!fileName || !fileContent) {
        return res.status(400).json({ hasError: true, compilerError: 'File name and content are required.' });
    }

    const safeFileName = fileName.replace(/[^a-zA-Z0-9_.-]/g, '');
    const fileExtension = path.extname(safeFileName).toLowerCase();

    if (!['.ts', '.cpp'].includes(fileExtension)) {
        return res.status(400).json({ hasError: true, compilerError: 'Unsupported file type. Only .ts and .cpp are allowed.' });
    }

    // Sanitize fileContent to prevent command injection
    const sanitizedFileContent = fileContent.replace(/[^a-zA-Z0-9_();{}=+\-*/\s]/g, '');
    const tempFilePath = path.join('/tmp', safeFileName);
    fs.writeFileSync(tempFilePath, sanitizedFileContent);

    let compileCommand;
    let args;
    if (fileExtension === '.ts') {
        compileCommand = 'tsc';
        args = [tempFilePath, '--noEmit'];
    } else if (fileExtension === '.cpp') {
        compileCommand = 'g++';
        args = [tempFilePath, '-o', path.join('/tmp', safeFileName.replace('.cpp', ''))];
    }

    execFile(compileCommand, args, (error, stdout, stderr) => {
        if (error) {
            return res.json({ hasError: true, compilerError: stderr || 'Compilation failed.' });
        }
        res.json({ hasError: false, compilerError: null });
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});