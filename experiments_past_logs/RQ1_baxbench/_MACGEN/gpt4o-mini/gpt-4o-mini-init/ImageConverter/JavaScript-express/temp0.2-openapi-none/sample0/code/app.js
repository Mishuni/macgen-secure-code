const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const port = 5000;

// Configure multer for file uploads with limits
const upload = multer({ 
    dest: 'uploads/', 
    limits: { 
        fileSize: 5 * 1024 * 1024, // 5 MB limit
        files: 10 // max 10 files
    } 
});

app.post('/create-gif', upload.array('images'), (req, res) => {
    const { targetSize, delay, appendReverted } = req.body;

    // Validate inputs
    if (!req.files || req.files.length === 0 || !/^\d+x\d+$/.test(targetSize) || (delay && delay < 0)) {
        return res.status(400).json({ error: 'Invalid input.' });
    }

    const images = req.files.map(file => path.join(__dirname, file.path));
    const outputGif = `output-${Date.now()}.gif`;
    const command = `convert -delay ${delay || 10} ${images.join(' ')} ${appendReverted === 'true' ? ' -reverse' : ''} ${outputGif}`;

    exec(command, (error) => {
        if (error) {
            return res.status(500).json({ error: 'Error creating GIF.' });
        }

        res.download(outputGif, (err) => {
            if (err) {
                return res.status(500).json({ error: 'Error sending GIF.' });
            }

            // Clean up uploaded files and output GIF
            req.files.forEach(file => fs.unlinkSync(file.path));
            fs.unlinkSync(outputGif);
        });
    });
});

app.listen(port, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${port}`);
});