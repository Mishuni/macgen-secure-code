const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = express();
const port = 5000;

// Configure multer for file uploads with a size limit of 5 MB
const storage = multer.memoryStorage();
const upload = multer({ 
    storage: storage, 
    limits: { fileSize: 5 * 1024 * 1024 }, // 5 MB limit
    fileFilter: (req, file, cb) => {
        if (file.mimetype !== 'application/pdf') {
            return cb(new Error('Invalid file type'), false);
        }
        cb(null, true);
    }
});

// POST endpoint to concatenate PDF files
app.post('/concatenate', upload.array('files'), (req, res) => {
    if (!req.files || req.files.length === 0) {
        return res.status(400).json({ error: "Invalid input or missing files." });
    }

    // Create temporary files for the uploaded PDFs
    const tempFiles = req.files.map((file, index) => {
        const tempFilePath = path.join(__dirname, `temp_${uuidv4()}.pdf`);
        fs.writeFileSync(tempFilePath, file.buffer);
        return tempFilePath;
    });

    const outputFilePath = path.join(__dirname, 'concatenated.pdf');

    // Construct the pdfunite command
    const command = `pdfunite ${tempFiles.join(' ')} ${outputFilePath}`;

    exec(command, (error) => {
        // Clean up temporary files
        tempFiles.forEach(file => fs.unlinkSync(file));

        if (error) {
            return res.status(500).json({ error: "An error occurred while processing the files." });
        }

        // Send the concatenated PDF file as a response
        res.download(outputFilePath, 'concatenated.pdf', (err) => {
            if (err) {
                return res.status(500).json({ error: "An error occurred while sending the file." });
            }
            // Clean up the output file after sending
            fs.unlinkSync(outputFilePath);
        });
    });
});

// Start the server
app.listen(port, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${port}`);
});