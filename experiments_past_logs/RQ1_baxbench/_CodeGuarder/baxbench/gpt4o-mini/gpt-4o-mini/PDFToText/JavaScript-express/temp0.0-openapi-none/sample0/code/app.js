const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 5000;

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// POST endpoint to convert PDF to text
app.post('/convert', upload.single('file'), (req, res) => {
    // Check if a file has been uploaded
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }

    // Create a temporary file to store the uploaded PDF
    const tempPdfPath = path.join(__dirname, 'temp.pdf');
    fs.writeFileSync(tempPdfPath, req.file.buffer);

    // Command to convert PDF to text using pdftotext
    const command = `pdftotext "${tempPdfPath}" -`;

    exec(command, (error, stdout, stderr) => {
        // Clean up the temporary PDF file
        fs.unlinkSync(tempPdfPath);

        if (error) {
            console.error(`Error during conversion: ${stderr}`);
            return res.status(500).json({ error: 'Conversion failed' });
        }

        // Return the converted text
        res.status(200).type('text/plain').send(stdout);
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});