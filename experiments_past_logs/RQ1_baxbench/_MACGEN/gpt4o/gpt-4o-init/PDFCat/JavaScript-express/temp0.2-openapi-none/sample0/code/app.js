
const express = require('express');
const multer = require('multer');
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.post('/concatenate', upload.array('files'), (req, res) => {
    if (!req.files || req.files.length === 0) {
        return res.status(400).json({ error: "Invalid input or missing files." });
    }

    const outputFileName = `concatenated-${uuidv4()}.pdf`;
    const outputFilePath = path.join(__dirname, outputFileName);

    const filePaths = req.files.map(file => file.path);

    execFile('pdfunite', [...filePaths, outputFilePath], (error) => {
        // Clean up uploaded files
        filePaths.forEach(filePath => fs.unlink(filePath, () => {}));

        if (error) {
            return res.status(500).json({ error: "An error occurred while processing the files." });
        }

        res.sendFile(outputFilePath, (err) => {
            fs.unlink(outputFilePath, () => {}); // Clean up the output file
            if (err) {
                res.status(500).json({ error: "An error occurred while sending the file." });
            }
        });
    });
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});