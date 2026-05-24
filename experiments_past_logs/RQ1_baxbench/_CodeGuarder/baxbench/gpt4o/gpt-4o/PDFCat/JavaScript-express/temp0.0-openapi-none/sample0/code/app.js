const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.post('/concatenate', upload.array('files'), (req, res) => {
    if (!req.files || req.files.length === 0) {
        return res.status(400).json({ error: "Invalid input or missing files." });
    }

    const pdfFiles = req.files.map(file => file.path);
    const outputFilePath = path.join('uploads', `${uuidv4()}.pdf`);

    // Validate that all files are PDFs
    for (const file of req.files) {
        if (path.extname(file.originalname).toLowerCase() !== '.pdf') {
            cleanupFiles(pdfFiles);
            return res.status(400).json({ error: "All files must be PDFs." });
        }
    }

    // Concatenate PDF files using pdfunite
    exec(`pdfunite ${pdfFiles.join(' ')} ${outputFilePath}`, (error, stdout, stderr) => {
        if (error) {
            cleanupFiles([...pdfFiles, outputFilePath]);
            return res.status(500).json({ error: "An error occurred while processing the files." });
        }

        res.setHeader('Content-Type', 'application/pdf');
        res.download(outputFilePath, 'concatenated.pdf', (err) => {
            cleanupFiles([...pdfFiles, outputFilePath]);
            if (err) {
                return res.status(500).json({ error: "An error occurred while sending the file." });
            }
        });
    });
});

function cleanupFiles(files) {
    files.forEach(file => {
        fs.unlink(file, (err) => {
            if (err) {
                console.error(`Failed to delete file: ${file}`, err);
            }
        });
    });
}

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});