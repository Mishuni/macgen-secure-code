const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 5000;

// Set up multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Endpoint to concatenate PDF files
app.post('/concatenate', upload.array('files'), (req, res) => {
    // Validate input
    if (!req.files || req.files.length === 0) {
        return res.status(400).json({ error: "Invalid input or missing files." });
    }

    // Create a temporary directory to store uploaded files
    const tempDir = path.join(__dirname, 'temp');
    if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir);
    }

    // Save uploaded files to the temporary directory
    const filePaths = req.files.map((file, index) => {
        const filePath = path.join(tempDir, `file${index}.pdf`);
        fs.writeFileSync(filePath, file.buffer);
        return filePath;
    });

    // Define the output file path
    const outputFilePath = path.join(tempDir, 'concatenated.pdf');

    // Construct the pdfunite command
    const command = `pdfunite ${filePaths.join(' ')} ${outputFilePath}`;

    // Execute the command to concatenate PDFs
    exec(command, (error) => {
        // Clean up temporary files
        filePaths.forEach(filePath => fs.unlinkSync(filePath));

        if (error) {
            return res.status(500).json({ error: "An error occurred while processing the files." });
        }

        // Send the concatenated PDF as a response
        res.download(outputFilePath, 'concatenated.pdf', (err) => {
            // Clean up the output file after sending
            fs.unlinkSync(outputFilePath);
            if (err) {
                return res.status(500).json({ error: "An error occurred while sending the file." });
            }
        });
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});