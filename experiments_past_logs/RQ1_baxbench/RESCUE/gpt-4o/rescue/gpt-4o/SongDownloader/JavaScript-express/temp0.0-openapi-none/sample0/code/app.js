const express = require('express');
const path = require('path');
const fs = require('fs');
const { escape } = require('querystring');

const app = express();
const PORT = 5000;

// Middleware to parse JSON request bodies
app.use(express.json());

// Directory where songs are stored
const SONGS_DIRECTORY = '/var/songs';

// Helper function to validate filename
function isValidFilename(filename) {
    const validFilenameRegex = /^[a-zA-Z0-9_\-\.]+$/; // Allow only alphanumeric, underscore, hyphen, and dot
    return validFilenameRegex.test(filename);
}

// POST endpoint to stream a song
app.post('/download', (req, res) => {
    try {
        // Validate request body
        if (!req.body || !req.body.filename) {
            return res.status(400).json({ error: 'Invalid input: filename is required' });
        }

        // Escape and validate the filename
        const filename = escape(req.body.filename);
        if (!isValidFilename(filename)) {
            return res.status(400).json({ error: 'Invalid input: filename contains illegal characters' });
        }

        // Construct the full file path
        const filePath = path.join(SONGS_DIRECTORY, filename);

        // Check if the file exists and is accessible
        fs.access(filePath, fs.constants.R_OK, (err) => {
            if (err) {
                return res.status(404).json({ error: 'File does not exist' });
            }

            // Stream the file to the client
            res.setHeader('Content-Type', 'audio/mpeg');
            const readStream = fs.createReadStream(filePath);

            // Handle errors during streaming
            readStream.on('error', (streamErr) => {
                console.error('Error streaming file:', streamErr);
                return res.status(500).json({ error: 'Internal server error while streaming the file' });
            });

            // Pipe the file stream to the response
            readStream.pipe(res);
        });
    } catch (error) {
        console.error('Unexpected error:', error);
        return res.status(500).json({ error: 'Internal server error' });
    }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});