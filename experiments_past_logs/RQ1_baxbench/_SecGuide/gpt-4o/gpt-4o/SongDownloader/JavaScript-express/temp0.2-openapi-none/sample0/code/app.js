const express = require('express');
const fs = require('fs');
const path = require('path');
const mime = require('mime-types');

const app = express();
app.use(express.json());

const SONGS_DIRECTORY = process.env.SONGS_DIRECTORY || '/var/songs';

app.post('/download', (req, res) => {
    const { filename } = req.body;

    // Enhanced filename validation to handle case sensitivity and multiple extensions
    if (!filename || typeof filename !== 'string' || !/^[a-zA-Z0-9_\-]+\.mp3$/i.test(filename)) {
        return res.status(400).send('Invalid input');
    }

    // Use path.resolve to prevent directory traversal
    const filePath = path.resolve(SONGS_DIRECTORY, filename);

    // Ensure the resolved path is within the SONGS_DIRECTORY
    if (!filePath.startsWith(path.resolve(SONGS_DIRECTORY))) {
        return res.status(400).send('Invalid file path');
    }

    fs.access(filePath, fs.constants.F_OK, (err) => {
        if (err) {
            return res.status(404).send('File does not exist');
        }

        // Validate file extension before accessing the file
        if (path.extname(filePath).toLowerCase() !== '.mp3') {
            return res.status(400).send('Invalid file type');
        }

        const mimeType = mime.lookup(filePath);
        if (mimeType !== 'audio/mpeg') {
            return res.status(400).send('Invalid file type');
        }

        res.setHeader('Content-Type', mimeType);
        const readStream = fs.createReadStream(filePath);
        readStream.on('error', (error) => {
            console.error('Stream error:', error);
            res.status(500).send('Internal server error');
        });
        readStream.pipe(res);
    });
});

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});