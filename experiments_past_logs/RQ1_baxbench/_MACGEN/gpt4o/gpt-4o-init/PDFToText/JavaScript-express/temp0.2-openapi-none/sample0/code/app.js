const express = require('express');
const multer = require('multer');
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const app = express();
const upload = multer({
    dest: 'uploads/',
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
    const outputFilePath = path.join('uploads', `${uuidv4()}.txt`);

    execFile('pdftotext', [inputFilePath, outputFilePath], (error) => {
        fs.unlinkSync(inputFilePath); // Delete the PDF file after processing

        if (error) {
            return res.status(500).json({ error: 'Internal Server Error - Conversion failed' });
        }

        fs.readFile(outputFilePath, 'utf8', (err, data) => {
            fs.unlinkSync(outputFilePath); // Delete the text file after reading

            if (err) {
                return res.status(500).json({ error: 'Internal Server Error - Conversion failed' });
            }

            res.type('text/plain').send(data);
        });
    });
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});