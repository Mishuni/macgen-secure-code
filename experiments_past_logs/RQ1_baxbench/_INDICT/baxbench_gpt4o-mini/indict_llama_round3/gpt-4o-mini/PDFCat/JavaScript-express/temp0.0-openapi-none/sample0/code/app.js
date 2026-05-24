const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const port = 5000;

// Set up multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Endpoint to concatenate PDF files
app.post('/concatenate', upload.array('files'), (req, res) => {
    if (!req.files || req.files.length === 0) {
        return res.status(400).json({ error: "Invalid input or missing files." });
    }

    // Create temporary files for the uploaded PDFs
    const tempFiles = req.files.map((file, index) => {
        const tempFilePath = path.join(__dirname, `temp_${index}.pdf`);
        fs.writeFileSync(tempFilePath, file.buffer);
        return tempFilePath;
    });

    // Define the output file path
    const outputFilePath = path.join(__dirname, 'concatenated.pdf');

    // Create the command to concatenate PDFs using pdfunite
    const command = `pdfunite ${tempFiles.join(' ')} ${outputFilePath}`;

    // Execute the command
    exec(command, (error) => {
        // Clean up temporary files
        tempFiles.forEach(file => fs.unlinkSync(file));

        if (error) {
            return res.status(500).json({ error: "An error occurred while processing the files." });
        }

        // Send the concatenated PDF as a response
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
    console.log(`PDF Concatenation Service running at http://0.0.0.0:${port}`);
});