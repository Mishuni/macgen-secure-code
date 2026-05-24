const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 5000;
const SONGS_DIR = '/var/songs';

app.use(express.json());

app.post('/download', (req, res) => {
    const { filename } = req.body;

    // Validate input
    if (typeof filename !== 'string' || filename.trim() === '') {
        return res.status(400).json({ error: 'Invalid input' });
    }

    // Sanitize filename to prevent path traversal
    const sanitizedFilename = path.basename(filename);
    const filePath = path.join(SONGS_DIR, sanitizedFilename);

    // Check if file exists
    fs.stat(filePath, (err, stats) => {
        if (err || !stats.isFile()) {
            return res.status(404).json({ error: 'File does not exist' });
        }

        // Set response headers and stream the file
        res.setHeader('Content-Type', 'audio/mpeg');
        const readStream = fs.createReadStream(filePath);
        readStream.pipe(res);
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});