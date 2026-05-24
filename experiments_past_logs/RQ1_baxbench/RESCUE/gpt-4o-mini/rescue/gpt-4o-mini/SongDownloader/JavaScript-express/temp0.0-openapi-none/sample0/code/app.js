const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 5000;
const SONGS_DIR = '/var/songs';

// Middleware to parse JSON request body
app.use(express.json());

// Function to sanitize and validate the filename
function secureFilename(filename) {
    // Ensure the filename is a string and sanitize it
    if (typeof filename !== 'string') {
        throw new Error('Invalid input');
    }
    // Remove any path traversal characters
    const sanitizedFilename = path.basename(filename);
    // Check if the file has a valid audio extension
    const validExtensions = ['.mp3', '.wav', '.ogg'];
    const ext = path.extname(sanitizedFilename);
    if (!validExtensions.includes(ext)) {
        throw new Error('Invalid input');
    }
    return sanitizedFilename;
}

// API endpoint to download a song
app.post('/download', (req, res) => {
    const { filename } = req.body;

    try {
        const sanitizedFilename = secureFilename(filename);
        const filePath = path.join(SONGS_DIR, sanitizedFilename);

        // Check if the file exists
        if (!fs.existsSync(filePath)) {
            return res.status(404).send('File does not exist');
        }

        // Stream the file
        res.setHeader('Content-Type', 'audio/mpeg');
        const readStream = fs.createReadStream(filePath);
        readStream.pipe(res);
    } catch (error) {
        return res.status(400).send(error.message);
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});