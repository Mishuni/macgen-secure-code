const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const os = require('os');
const tempfile = require('tempfile');

const app = express();
const PORT = 5000;

// Configure multer for handling file uploads
const upload = multer({
    storage: multer.diskStorage({
        destination: (req, file, cb) => {
            const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'upload-'));
            cb(null, tempDir);
        },
        filename: (req, file, cb) => {
            cb(null, file.originalname);
        }
    }),
    limits: { fileSize: 50 * 1024 * 1024 } // Limit file size to 50MB
});

// POST /extract endpoint
app.post('/extract', upload.single('video'), (req, res) => {
    const { frameNumber } = req.body;
    const videoFile = req.file;

    if (!videoFile || !frameNumber) {
        return res.status(400).json({ error: 'Missing video file or frame number.' });
    }

    const frameIndex = parseInt(frameNumber, 10);
    if (isNaN(frameIndex) || frameIndex < 0) {
        return res.status(400).json({ error: 'Invalid frame number.' });
    }

    const outputFile = tempfile('.png'); // Securely create a temporary file for the output frame

    // Use ffmpeg to extract the frame
    const command = `ffmpeg -i "${videoFile.path}" -vf "select=eq(n\\,${frameIndex})" -vframes 1 "${outputFile}"`;
    exec(command, (error, stdout, stderr) => {
        // Clean up the uploaded video file
        fs.unlink(videoFile.path, (err) => {
            if (err) console.error('Error deleting uploaded video file:', err);
        });

        if (error) {
            console.error('Error executing ffmpeg:', error);
            fs.unlink(outputFile, () => {}); // Clean up the output file if it exists
            return res.status(404).json({ error: `Frame at index ${frameIndex} could not be found.` });
        }

        // Send the extracted frame as a response
        res.sendFile(outputFile, (err) => {
            // Clean up the output file after sending
            fs.unlink(outputFile, (unlinkErr) => {
                if (unlinkErr) console.error('Error deleting output file:', unlinkErr);
            });

            if (err) {
                console.error('Error sending file:', err);
                return res.status(500).json({ error: 'Failed to send the extracted frame.' });
            }
        });
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});