const express = require('express');
const multer = require('multer');
const unzipper = require('unzipper');
const { Readable } = require('stream');

const app = express();
const port = 5000;

// Set up multer for file upload
const upload = multer({ limits: { fileSize: 10 * 1024 * 1024 } }); // Limit to 10MB

app.post('/convert', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).send('Invalid input: No file uploaded.');
    }

    const zipFileStream = Readable.from(req.file.buffer);
    let combinedText = '';

    zipFileStream
        .pipe(unzipper.Parse())
        .on('entry', (entry) => {
            if (entry.type === 'File' && entry.path.endsWith('.txt')) {
                entry.buffer().then((buffer) => {
                    combinedText += buffer.toString('utf-8') + '\n'; // Concatenate text files
                });
            } else {
                entry.autodrain(); // Skip non-text files
            }
        })
        .on('finish', () => {
            res.setHeader('Content-Type', 'text/plain');
            res.send(combinedText);
        })
        .on('error', (err) => {
            console.error(err);
            res.status(400).send('Error processing the zip file.');
        });
});

app.listen(port, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${port}`);
});