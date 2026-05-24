const express = require('express');
const fs = require('fs');
const path = require('path');
const mime = require('mime-types'); // Import mime-types package for dynamic content type
const app = express();
const PORT = 5000;

// Middleware to parse JSON request body
app.use(express.json());

// Function to validate the filename
const isValidFilename = (filename) => {
    const regex = /^[a-zA-Z0-9._-]+$/; // Allow only alphanumeric characters, dots, underscores, and dashes
    return regex.test(filename);
};

// Endpoint to download a song
app.post('/download', (req, res) => {
    const { filename } = req.body;

    // Validate the filename input
    if (typeof filename !== 'string' || filename.trim() === '' || !isValidFilename(filename)) {
        return res.status(400).send('Invalid input');
    }

    // Sanitize the filename to prevent directory traversal attacks
    const sanitizedFilename = path.basename(filename);
    const filePath = path.join(__dirname, 'songs', sanitizedFilename); // Use __dirname for relative path

    // Check if the file exists and is readable
    fs.stat(filePath, (err, stats) => {
        if (err || !stats.isFile()) {
            return res.status(404).send('File not found');
        }

        // Validate MIME type based on file content
        const contentType = mime.lookup(sanitizedFilename) || 'application/octet-stream'; // Dynamically set content type
        res.setHeader('Content-Type', contentType);
        res.setHeader('Content-Disposition', `attachment; filename="${encodeURIComponent(sanitizedFilename)}"`); // Properly encode filename

        // Stream the file to the response
        const readStream = fs.createReadStream(filePath);
        readStream.on('error', (streamErr) => {
            console.error('Stream error:', streamErr); // Log the error for debugging
            res.status(500).send('Internal server error');
        });
        readStream.pipe(res);
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});