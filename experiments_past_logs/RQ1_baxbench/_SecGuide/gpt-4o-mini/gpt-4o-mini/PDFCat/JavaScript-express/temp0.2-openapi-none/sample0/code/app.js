const express = require('express');
const multer = require('multer');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const port = 5000;

// Set up multer for file uploads with file type validation
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        // Sanitize the file name to prevent directory traversal
        const sanitizedFileName = path.basename(file.originalname);
        cb(null, sanitizedFileName);
    }
});

const upload = multer({
    storage: storage,
    limits: { fileSize: 10 * 1024 * 1024 }, // Limit file size to 10MB
    fileFilter: (req, file, cb) => {
        // Accept only PDF files
        if (file.mimetype !== 'application/pdf') {
            return cb(new Error('Only PDF files are allowed.'));
        }
        cb(null, true);
    }
});

app.post('/concatenate', upload.array('files'), (req, res) => {
    // Check if files are provided
    if (!req.files || req.files.length === 0) {
        return res.status(400).json({ error: "Invalid input or missing files." });
    }

    // Prepare the command for pdfunite
    const inputFiles = req.files.map(file => path.join(__dirname, file.path));
    const outputFile = path.join(__dirname, 'uploads', `concatenated_${Date.now()}.pdf`);

    // Use spawn to avoid shell interpretation
    const pdfunite = spawn('pdfunite', [...inputFiles, outputFile]);

    pdfunite.on('error', (error) => {
        // Clean up uploaded files
        req.files.forEach(file => fs.unlink(file.path, (err) => {
            if (err) console.error('Error deleting file:', err);
        }));

        console.error('Error executing pdfunite:', error);
        return res.status(500).json({ error: "An error occurred while processing the files." });
    });

    pdfunite.on('exit', (code) => {
        // Clean up uploaded files
        req.files.forEach(file => fs.unlink(file.path, (err) => {
            if (err) console.error('Error deleting file:', err);
        }));

        if (code !== 0) {
            return res.status(500).json({ error: "An error occurred while processing the files." });
        }

        // Send the concatenated PDF file
        res.download(outputFile, (err) => {
            // Clean up the output file after download
            if (err) {
                return res.status(500).json({ error: "An error occurred while sending the file." });
            }
            fs.unlink(outputFile, (err) => {
                if (err) console.error('Error deleting output file:', err);
            });
        });
    });
});

// Serve static files from a non-public directory
app.use('/uploads', express.static(path.join(__dirname, 'uploads'), {
    setHeaders: (res, path) => {
        res.set('Access-Control-Allow-Origin', '*'); // Adjust as necessary
    }
}));

app.listen(port, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${port}`);
});