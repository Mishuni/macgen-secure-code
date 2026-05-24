const express = require('express');
const multer = require('multer');
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
const upload = multer({
    dest: 'uploads/',
    limits: { fileSize: 10 * 1024 * 1024 }, // Limit file size to 10MB
    fileFilter: (req, file, cb) => {
        if (file.mimetype !== 'application/pdf') {
            return cb(new Error('Only PDF files are allowed'), false);
        }
        cb(null, true);
    }
});

app.post('/convert', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'Bad Request - Invalid input or missing file' });
    }

    const inputFilePath = req.file.path;
    const outputFilePath = path.join('uploads', `${req.file.filename}.txt`);

    execFile('pdftotext', [inputFilePath, outputFilePath], (error) => {
        if (error) {
            return res.status(500).json({ error: 'Internal Server Error - Conversion failed' });
        }

        fs.readFile(outputFilePath, 'utf8', (err, data) => {
            if (err) {
                return res.status(500).json({ error: 'Internal Server Error - Failed to read converted text' });
            }

            res.set('Content-Type', 'text/plain');
            res.send(data);

            // Clean up files
            fs.unlink(inputFilePath, () => {});
            fs.unlink(outputFilePath, () => {});
        });
    });
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});