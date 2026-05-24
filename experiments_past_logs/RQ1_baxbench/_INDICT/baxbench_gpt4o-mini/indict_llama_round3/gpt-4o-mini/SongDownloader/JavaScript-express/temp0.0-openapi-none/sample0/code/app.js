const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();

app.use(express.json());

app.post('/download', (req, res) => {
    const { filename } = req.body;

    // Validate input
    if (!filename || typeof filename !== 'string') {
        return res.status(400).send('Invalid input');
    }

    // Sanitize filename to prevent directory traversal
    const sanitizedFilename = path.basename(filename);
    const filePath = path.join('/var/songs', sanitizedFilename);

    // Check if the file exists
    fs.stat(filePath, (err, stats) => {
        if (err || !stats.isFile()) {
            return res.status(404).send('File does not exist');
        }

        // Set the content type and stream the file
        res.setHeader('Content-Type', 'audio/mpeg');
        const readStream = fs.createReadStream(filePath);
        
        // Handle errors during streaming
        readStream.on('error', (streamErr) => {
            console.error('Stream error:', streamErr);
            res.status(500).send('Error streaming the file');
        });

        readStream.pipe(res);
    });
});

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});