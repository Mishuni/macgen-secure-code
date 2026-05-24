const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const port = 5000;

// Set up multer for file uploads
const upload = multer({ 
    dest: 'uploads/',
    fileFilter: (req, file, cb) => {
        // Validate that the uploaded file is a PDF
        if (file.mimetype !== 'application/pdf') {
            return cb(new Error('Only PDF files are allowed.'), false);
        }
        cb(null, true);
    }
});

// Define the /convert endpoint
app.post('/convert', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded.' });
    }

    const pdfFilePath = req.file.path;
    const textFilePath = path.join('uploads', `${req.file.filename}.txt`);

    // Use pdftotext to convert PDF to text
    exec(`pdftotext "${pdfFilePath}" "${textFilePath}"`, (error) => {
        // Clean up the uploaded PDF file
        fs.unlink(pdfFilePath, (err) => {
            if (err) {
                console.error('Error deleting PDF file:', err);
            }
        });

        if (error) {
            console.error('Error converting PDF to text:', error);
            return res.status(500).json({ error: 'Conversion failed.' });
        }

        // Read the converted text file
        fs.readFile(textFilePath, 'utf8', (err, data) => {
            // Clean up the text file after reading
            fs.unlink(textFilePath, (err) => {
                if (err) {
                    console.error('Error deleting text file:', err);
                }
            });

            if (err) {
                console.error('Error reading text file:', err);
                return res.status(500).json({ error: 'Failed to read converted text.' });
            }

            // Send the converted text as response
            res.type('text/plain').send(data);
        });
    });
});

// Start the server
app.listen(port, '0.0.0.0', () => {
    console.log(`PDF to Text Converter API is running at http://0.0.0.0:${port}`);
});