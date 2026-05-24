const express = require('express');
const { exec } = require('child_process');

const app = express();
const PORT = 5000;

app.use(express.json());

app.post('/compile', (req, res) => {
    const { fileName, fileContent } = req.body;

    // Validate content-type
    if (!req.is('application/json')) {
        return res.status(400).json({ hasError: true, compilerError: 'Invalid Content-Type' });
    }

    // Validate fileName and fileContent
    if (typeof fileName !== 'string' || typeof fileContent !== 'string') {
        return res.status(400).json({ hasError: true, compilerError: 'Invalid input data' });
    }

    // Determine the programming language based on the file extension
    const fileExtension = fileName.split('.').pop();
    let compileCommand;

    if (fileExtension === 'ts') {
        compileCommand = `tsc ${fileName}`;
    } else if (fileExtension === 'cpp') {
        compileCommand = `g++ ${fileName} -o output`;
    } else {
        return res.status(400).json({ hasError: true, compilerError: 'Unsupported file type' });
    }

    // Create a temporary file to hold the code
    const fs = require('fs');
    const path = require('path');
    const tempFilePath = path.join(__dirname, fileName);

    fs.writeFile(tempFilePath, fileContent, (err) => {
        if (err) {
            return res.status(500).json({ hasError: true, compilerError: 'Failed to write temporary file' });
        }

        // Execute the compile command
        exec(compileCommand, (error, stdout, stderr) => {
            // Clean up the temporary file
            fs.unlink(tempFilePath, (unlinkErr) => {
                if (unlinkErr) {
                    console.error('Failed to delete temporary file:', unlinkErr);
                }
            });

            if (error) {
                return res.json({ hasError: true, compilerError: stderr || 'Compilation failed' });
            }

            res.json({ hasError: false, compilerError: null });
        });
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});