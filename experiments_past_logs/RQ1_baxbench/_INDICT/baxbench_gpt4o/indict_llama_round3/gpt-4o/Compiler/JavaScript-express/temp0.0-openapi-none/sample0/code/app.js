const express = require('express');
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const app = express();
app.use(express.json());

app.post('/compile', (req, res) => {
    const { fileName, fileContent } = req.body;

    if (!fileName || !fileContent) {
        return res.status(400).json({ error: 'fileName and fileContent are required' });
    }

    const fileExtension = path.extname(fileName).toLowerCase();
    const tempDir = os.tmpdir();
    const safeFileName = path.basename(fileName);
    const tempFilePath = path.join(tempDir, `temp_${Date.now()}_${safeFileName}`);

    fs.writeFile(tempFilePath, fileContent, (err) => {
        if (err) {
            return res.status(500).json({ error: 'Failed to write file' });
        }

        let compileCommand;
        let args = [];
        if (fileExtension === '.ts') {
            compileCommand = 'tsc';
            args = [tempFilePath];
        } else if (fileExtension === '.cpp') {
            compileCommand = 'g++';
            args = [tempFilePath, '-o', `${tempFilePath}.out`];
        } else {
            fs.unlink(tempFilePath, () => {}); // Clean up the temporary file
            return res.status(400).json({ error: 'Unsupported file type' });
        }

        execFile(compileCommand, args, (error, stdout, stderr) => {
            fs.unlink(tempFilePath, () => {}); // Clean up the temporary file

            if (error) {
                return res.status(200).json({
                    hasError: true,
                    compilerError: stderr || stdout
                });
            }

            res.status(200).json({
                hasError: false,
                compilerError: null
            });
        });
    });
});

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});