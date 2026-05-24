const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const app = express();
const port = 5000;

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({
    storage: storage,
    limits: {
        fileSize: 5 * 1024 * 1024, // Limit file size to 5MB
        files: 10 // Limit number of files to 10
    }
});

// Middleware for error handling
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Internal Server Error' });
});

// POST endpoint to create GIF
app.post('/create-gif', upload.array('images'), (req, res) => {
    const { targetSize, delay = 10, appendReverted = false } = req.body;

    // Validate request body
    if (!req.files || req.files.length === 0) {
        return res.status(400).json({ error: 'Images are required.' });
    }
    if (!targetSize || !/^\d+x\d+$/.test(targetSize)) {
        return res.status(400).json({ error: 'Invalid targetSize format. Use width x height.' });
    }

    const imagePaths = req.files.map(file => `-`); // Use '-' to read from stdin
    const command = `convert ${imagePaths.join(' ')} -resize ${targetSize} -delay ${delay} ${appendReverted ? '-duplicate 1,-1' : ''} output.gif`;

    // Execute ImageMagick command
    exec(command, { input: Buffer.concat(req.files.map(file => file.buffer)) }, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error creating GIF: ${stderr}`);
            return res.status(500).json({ error: 'Failed to create GIF.' });
        }
        res.set('Content-Type', 'image/gif');
        res.send(stdout);
    });
});

// Start the server
app.listen(port, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${port}`);
});