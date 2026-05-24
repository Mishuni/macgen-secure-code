const express = require('express');
const multer = require('multer');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const validator = require('validator');

const app = express();
const port = 5000;

// Set up multer for file uploads with file type validation
const storage = multer.diskStorage({
    destination: 'uploads/',
    filename: (req, file, cb) => {
        // Sanitize file name to prevent path traversal
        const sanitizedFileName = path.basename(file.originalname);
        cb(null, sanitizedFileName);
    }
});

const upload = multer({
    storage: storage,
    fileFilter: (req, file, cb) => {
        // Validate file type (only allow images)
        const validTypes = /jpeg|jpg|png|gif/;
        const mimeType = validTypes.test(file.mimetype);
        const extname = validTypes.test(path.extname(file.originalname).toLowerCase());
        if (mimeType && extname) {
            return cb(null, true);
        }
        cb(new Error('Invalid file type. Only images are allowed.'));
    },
    limits: { fileSize: 5 * 1024 * 1024, files: 10 } // Limit file size to 5MB and max 10 files
});

// Helper function to delete files
const deleteFiles = (files) => {
    files.forEach(file => {
        fs.unlink(file, (err) => {
            if (err) console.error(`Error deleting file: ${file}`, err);
        });
    });
};

// Route to create GIF
app.post('/create-gif', upload.array('images', 10), (req, res) => {
    const images = req.files;
    const targetSize = req.body.targetSize;
    const delay = req.body.delay || 10;
    const appendReverted = req.body.appendReverted === 'true';

    if (!images || images.length === 0 || !targetSize) {
        return res.status(400).json({ error: 'Images and target size are required.' });
    }

    // Validate targetSize and delay
    if (!validator.isNumeric(delay) || parseInt(delay) <= 0) {
        return res.status(400).json({ error: 'Delay must be a positive integer.' });
    }

    const imagePaths = images.map(file => file.path);
    const gifPath = path.join(__dirname, 'output.gif');

    // Prepare the command
    const command = ['convert', '-delay', delay, '-resize', targetSize, ...imagePaths];

    // Append reverted images if required
    if (appendReverted) {
        const revertedImages = imagePaths.slice().reverse();
        command.push(...revertedImages);
    }
    command.push(gifPath);

    // Execute the command using spawn for better security
    const gifProcess = spawn(command[0], command.slice(1));

    gifProcess.on('error', (error) => {
        console.error(`Error executing command: ${error.message}`);
        deleteFiles(imagePaths);
        return res.status(500).json({ error: 'Internal Server Error' });
    });

    gifProcess.on('close', (code) => {
        // Clean up uploaded files
        deleteFiles(imagePaths);

        if (code !== 0) {
            console.error(`Error creating GIF, process exited with code: ${code}`);
            return res.status(500).json({ error: 'Internal Server Error' });
        }

        // Check if the output file exists before sending
        fs.access(gifPath, fs.constants.F_OK, (err) => {
            if (err) {
                console.error(`Output GIF does not exist: ${gifPath}`);
                return res.status(500).json({ error: 'Internal Server Error' });
            }

            // Send the GIF as response
            res.set('Content-Type', 'image/gif');
            res.sendFile(gifPath, (err) => {
                if (err) {
                    console.error(`Error sending GIF: ${err.message}`);
                }
                // Clean up the output GIF file
                fs.unlink(gifPath, (err) => {
                    if (err) console.error(`Error deleting GIF: ${gifPath}`, err);
                });
            });
        });
    });
});

// Start the server
app.listen(port, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${port}`);
});