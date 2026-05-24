const express = require('express');
const multer = require('multer');
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;

// Configure multer for file uploads
const upload = multer({
    dest: 'uploads/', // Temporary directory for uploaded files
    limits: {
        fileSize: 10 * 1024 * 1024 // Limit file size to 10MB
    },
    fileFilter: (req, file, cb) => {
        if (file.mimetype !== 'application/pdf') {
            return cb(new Error('Only PDF files are allowed'));
        }
        cb(null, true);
    }
});

// Utility function to safely delete files
const safeDeleteFile = (filePath) => {
    fs.unlink(filePath, (err) => {
        if (err) {
            console.error(`Failed to delete file: ${filePath}`, err);
        }
    });
};

// POST /convert endpoint
app.post('/convert', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded or invalid file format' });
    }

    const uploadedFilePath = req.file.path;
    const outputFilePath = `${uploadedFilePath}.txt`;

    // Use pdftotext to extract text from the PDF
    execFile('pdftotext', [uploadedFilePath, outputFilePath], (err) => {
        // Clean up the uploaded file
        safeDeleteFile(uploadedFilePath);

        if (err) {
            console.error('Error during PDF to text conversion:', err);
            return res.status(500).json({ error: 'Failed to convert PDF to text' });
        }

        // Read the output text file
        fs.readFile(outputFilePath, 'utf8', (readErr, data) => {
            // Clean up the output file
            safeDeleteFile(outputFilePath);

            if (readErr) {
                console.error('Error reading the converted text file:', readErr);
                return res.status(500).json({ error: 'Failed to read converted text' });
            }

            // Send the extracted text as plain text response
            res.type('text/plain').send(data);
        });
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    if (err instanceof multer.MulterError) {
        // Handle multer-specific errors
        return res.status(400).json({ error: err.message });
    } else if (err) {
        // Handle other errors
        console.error('Unhandled error:', err);
        return res.status(500).json({ error: 'Internal Server Error' });
    }
    next();
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});