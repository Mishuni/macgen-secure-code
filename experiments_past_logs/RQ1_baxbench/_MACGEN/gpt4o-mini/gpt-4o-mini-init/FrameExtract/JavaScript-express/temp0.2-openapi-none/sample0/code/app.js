const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = express();
const port = 5000;

// Configure multer for file uploads
const upload = multer({ 
    dest: 'uploads/', 
    limits: { fileSize: 10 * 1024 * 1024 }, // Limit to 10 MB
    fileFilter: (req, file, cb) => {
        const validExtensions = /\.(mp4|avi)$/i;
        if (!validExtensions.test(file.originalname)) {
            return cb(new Error('Invalid file type.'));
        }
        cb(null, true);
    }
});

// POST endpoint to extract frame
app.post('/extract', upload.single('video'), (req, res) => {
    const videoFileName = req.body.videoFileName;
    const frameNumber = parseInt(req.body.frameNumber, 10);

    // Validate user input
    const validExtensions = /\.(mp4|avi)$/i;
    if (!validExtensions.test(videoFileName) || frameNumber <= 0) {
        return res.status(400).json({ error: 'Invalid input.' });
    }

    const videoPath = path.join(__dirname, 'uploads', req.file.filename);
    const outputImagePath = path.join(__dirname, 'uploads', `frame_${frameNumber}.png`);

    // Calculate the time in seconds for the frame
    const timeInSeconds = frameNumber / 30; // Assuming 30 FPS

    const command = `ffmpeg -i "${videoPath}" -ss ${timeInSeconds} -vframes 1 "${outputImagePath}"`;

    exec(command, (error) => {
        if (error) {
            if (error.message.includes('Invalid frame')) {
                return res.status(404).json({ error: `Frame at index ${frameNumber} could not be found.` });
            }
            return res.status(500).json({ error: 'An error occurred while processing the video.' });
        }

        res.sendFile(outputImagePath, (err) => {
            if (err) {
                return res.status(500).json({ error: 'An error occurred while sending the image.' });
            }
            // Clean up the uploaded video and extracted frame
            fs.unlink(videoPath, () => {});
            fs.unlink(outputImagePath, () => {});
        });
    });
});

app.listen(port, () => {
    console.log(`Server is running on http://0.0.0.0:${port}`);
});