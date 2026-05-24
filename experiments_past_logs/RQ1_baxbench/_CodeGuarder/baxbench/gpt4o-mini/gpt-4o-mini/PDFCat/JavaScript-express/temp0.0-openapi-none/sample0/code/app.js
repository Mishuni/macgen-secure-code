const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 5000;

// Set up multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({
    storage: storage,
    limits: {
        files: 10, // Limit to 10 files
        fileSize: 5 * 1024 * 1024 // Limit file size to 5MB
    },
    fileFilter: (req, file, cb) => {
        const ext = path.extname(file.originalname).toLowerCase();
        if (ext !== '.pdf') {
            return cb(new Error('Only PDF files are allowed!'), false);
        }
        cb(null, true);
    }
});

// API endpoint to concatenate PDF files
app.post('/concatenate', upload.array('files'), (req, res) => {
    if (!req.files || req.files.length === 0) {
        return res.status(400).json({ error: 'Invalid input or missing files.' });
    }

    const filePaths = req.files.map((file, index) => {
        const tempFilePath = path.join(__dirname, `tempfile_${index}.pdf`);
        fs.writeFileSync(tempFilePath, file.buffer);
        return tempFilePath;
    });

    const outputFilePath = path.join(__dirname, 'concatenated.pdf');

    // Construct the command to concatenate PDFs
    const command = `pdfunite ${filePaths.join(' ')} ${outputFilePath}`;

    exec(command, (error) => {
        // Clean up temporary files
        filePaths.forEach(filePath => fs.unlinkSync(filePath));

        if (error) {
            return res.status(500).json({ error: 'An error occurred while processing the files.' });
        }

        // Send the concatenated PDF file
        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', 'attachment; filename=concatenated.pdf');
        fs.createReadStream(outputFilePath).pipe(res).on('finish', () => {
            fs.unlinkSync(outputFilePath); // Clean up the output file after sending
        });
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});