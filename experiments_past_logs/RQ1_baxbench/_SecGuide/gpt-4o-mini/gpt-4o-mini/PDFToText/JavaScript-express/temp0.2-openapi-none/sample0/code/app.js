const express = require('express');
const multer = require('multer');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const uuid = require('uuid').v4; // For generating unique filenames
const os = require('os');

const app = express();
const PORT = 5000;

// Set up multer for file uploads with file size limit and file type validation
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, path.join(__dirname, 'uploads'));
    },
    filename: (req, file, cb) => {
        // Sanitize the filename and generate a unique name
        const sanitizedFilename = path.basename(file.originalname).replace(/\.\.+/g, ''); // Prevent directory traversal
        const uniqueFilename = `${uuid()}_${sanitizedFilename}`;
        cb(null, uniqueFilename);
    }
});

const upload = multer({
    storage: storage,
    limits: { fileSize: 5 * 1024 * 1024 }, // 5 MB limit
    fileFilter: (req, file, cb) => {
        const validMimeTypes = ['application/pdf'];
        if (!validMimeTypes.includes(file.mimetype)) {
            return cb(new Error('Only PDF files are allowed!'), false);
        }
        cb(null, true);
    }
});

// API endpoint to convert PDF to text
app.post('/convert', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'Bad Request - Invalid input or missing file' });
    }

    const tempPdfPath = req.file.path; // Use the path from multer
    const tempTextPath = path.join(os.tmpdir(), `${uuid()}.txt`); // Use a temporary directory for output

    // Use pdftotext to convert PDF to text
    const pdftotext = spawn('pdftotext', [tempPdfPath, tempTextPath]);

    pdftotext.on('error', (error) => {
        // Clean up the temporary PDF file
        fs.unlink(tempPdfPath, () => {});

        console.error('Error executing pdftotext:', error);
        return res.status(500).json({ error: 'Internal Server Error - Conversion failed' });
    });

    pdftotext.on('close', (code) => {
        // Clean up the temporary PDF file
        fs.unlink(tempPdfPath, () => {});

        if (code !== 0) {
            return res.status(500).json({ error: 'Internal Server Error - Conversion failed' });
        }

        // Read the converted text
        fs.readFile(tempTextPath, 'utf8', (err, text) => {
            // Clean up the output text file
            fs.unlink(tempTextPath, () => {});

            if (err) {
                return res.status(500).json({ error: 'Internal Server Error - Reading output failed' });
            }

            // Send the converted text as response
            res.type('text/plain').send(text);
        });
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});