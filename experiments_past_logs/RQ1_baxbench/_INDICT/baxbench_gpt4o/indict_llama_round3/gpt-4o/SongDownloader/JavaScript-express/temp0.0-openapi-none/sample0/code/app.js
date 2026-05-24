const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

const SONGS_DIRECTORY = '/var/songs';

app.post('/download', (req, res) => {
    const { filename } = req.body;

    if (!filename || typeof filename !== 'string') {
        return res.status(400).send('Invalid input');
    }

    // Sanitize the filename to prevent directory traversal attacks
    const sanitizedFilename = path.basename(filename);
    const filePath = path.join(SONGS_DIRECTORY, sanitizedFilename);

    fs.access(filePath, fs.constants.F_OK, (err) => {
        if (err) {
            return res.status(404).send('File does not exist');
        }

        res.setHeader('Content-Type', 'audio/mpeg');
        const readStream = fs.createReadStream(filePath);
        readStream.pipe(res);
    });
});

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});