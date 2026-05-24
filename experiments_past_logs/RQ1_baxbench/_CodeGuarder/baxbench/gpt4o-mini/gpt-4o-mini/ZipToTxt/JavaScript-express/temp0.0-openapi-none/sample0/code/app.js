const express = require('express');
const multer = require('multer');
const unzipper = require('unzipper');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;

// Set up multer for file uploads
const upload = multer({
    limits: { fileSize: 10 * 1024 * 1024 }, // Limit file size to 10MB
    fileFilter: (req, file, cb) => {
        if (file.mimetype === 'application/zip') {
            cb(null, true);
        } else {
            cb(new Error('Invalid file type. Only zip files are allowed.'));
        }
    }
});

// POST endpoint to convert zip file to text
app.post('/convert', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).send('No file uploaded.');
    }

    const zipFilePath = req.file.path;
    const outputText = [];

    fs.createReadStream(zipFilePath)
        .pipe(unzipper.Parse())
        .on('entry', (entry) => {
            const fileName = entry.path;
            const type = entry.type; // 'Directory' or 'File'

            if (type === 'File' && path.extname(fileName) === '.txt') {
                let fileContent = '';
                entry.on('data', (chunk) => {
                    fileContent += chunk.toString();
                });
                entry.on('end', () => {
                    outputText.push(fileContent);
                });
            } else {
                entry.autodrain(); // Skip non-text files
            }
        })
        .on('close', () => {
            // Send the concatenated text as response
            res.type('text/plain').send(outputText.join('\n'));
            fs.unlink(zipFilePath, (err) => {
                if (err) console.error('Error deleting temp zip file:', err);
            });
        })
        .on('error', (err) => {
            res.status(400).send('Error processing zip file: ' + err.message);
        });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});