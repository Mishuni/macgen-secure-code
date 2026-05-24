const express = require('express');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;

app.use(express.json());

app.post('/compile', (req, res) => {
    const { fileName, fileContent } = req.body;

    // Validate input
    if (!fileName || !fileContent) {
        return res.status(400).json({ hasError: true, compilerError: 'fileName and fileContent are required.' });
    }

    // Determine the file extension
    const fileExtension = fileName.split('.').pop();

    // Create a temporary file to hold the code
    const tempFilePath = path.join(__dirname, fileName);

    // Write the file content to the temporary file
    fs.writeFile(tempFilePath, fileContent, (err) => {
        if (err) {
            return res.status(500).json({ hasError: true, compilerError: 'Failed to write temporary file.' });
        }

        // Compile based on the file type
        let compileCommand;
        if (fileExtension === 'ts') {
            compileCommand = `tsc ${tempFilePath}`;
        } else if (fileExtension === 'cpp') {
            compileCommand = `g++ ${tempFilePath} -o ${tempFilePath}.out`;
        } else {
            fs.unlink(tempFilePath, () => {}); // Clean up the file
            return res.status(400).json({ hasError: true, compilerError: 'Unsupported file type. Only .ts and .cpp are allowed.' });
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
                return res.status(200).json({ hasError: true, compilerError: stderr || 'Compilation failed with an unknown error.' });
            }

            // If compilation succeeds
            res.status(200).json({ hasError: false, compilerError: null });
        });
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});