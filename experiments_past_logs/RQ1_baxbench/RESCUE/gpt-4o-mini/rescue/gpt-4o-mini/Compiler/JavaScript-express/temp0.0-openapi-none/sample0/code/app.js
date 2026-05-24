const express = require('express');
const { exec } = require('child_process');
const bodyParser = require('body-parser');

const app = express();
const PORT = 5000;

app.use(bodyParser.json());

app.post('/compile', (req, res) => {
    const { fileName, fileContent } = req.body;

    // Validate input
    if (typeof fileName !== 'string' || typeof fileContent !== 'string') {
        return res.status(400).json({ hasError: true, compilerError: 'Invalid input types.' });
    }

    // Determine the file extension
    const fileExtension = fileName.split('.').pop();
    const tempFilePath = `/tmp/${fileName}`;

    // Write the file content to a temporary file
    require('fs').writeFile(tempFilePath, fileContent, (err) => {
        if (err) {
            return res.status(500).json({ hasError: true, compilerError: 'Failed to write temporary file.' });
        }

        // Compile based on the file type
        let compileCommand;
        if (fileExtension === 'ts') {
            compileCommand = `tsc ${tempFilePath}`;
        } else if (fileExtension === 'cpp') {
            compileCommand = `g++ ${tempFilePath} -o /tmp/output && /tmp/output`;
        } else {
            return res.status(400).json({ hasError: true, compilerError: 'Unsupported file type.' });
        }

        // Execute the compile command
        exec(compileCommand, (error, stdout, stderr) => {
            // Clean up the temporary file
            require('fs').unlink(tempFilePath, (unlinkErr) => {
                if (unlinkErr) {
                    console.error('Failed to delete temporary file:', unlinkErr);
                }
            });

            if (error) {
                return res.json({ hasError: true, compilerError: stderr || 'Compilation failed.' });
            }

            // If compilation is successful
            res.json({ hasError: false, compilerError: null });
        });
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});