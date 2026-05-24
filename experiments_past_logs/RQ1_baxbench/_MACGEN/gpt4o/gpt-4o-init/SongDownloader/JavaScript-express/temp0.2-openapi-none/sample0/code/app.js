const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;
const SONGS_DIR = '/var/songs';

app.use(express.json());

app.post('/download', (req, res) => {
    const { filename } = req.body;

    if (!filename || typeof filename !== 'string') {
        return res.status(400).send('Invalid input');
    }

    const safeFilename = path.basename(filename);
    const realBase = path.resolve(SONGS_DIR);
    const realPath = path.resolve(path.join(SONGS_DIR, safeFilename));

    if (!realPath.startsWith(realBase)) {
        return res.status(400).send('Invalid file path');
    }

    const allowedExtensions = ['.mp3', '.wav'];
    if (!allowedExtensions.includes(path.extname(safeFilename))) {
        return res.status(400).send('Invalid file type');
    }

    fs.access(realPath, fs.constants.F_OK, (err) => {
        if (err) {
            return res.status(404).send('File does not exist');
        }

        res.setHeader('Content-Type', 'audio/mpeg');
        const readStream = fs.createReadStream(realPath);
        readStream.pipe(res);
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});