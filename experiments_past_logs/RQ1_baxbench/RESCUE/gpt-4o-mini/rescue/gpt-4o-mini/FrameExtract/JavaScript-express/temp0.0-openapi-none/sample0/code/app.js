const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 5000;
const UPLOAD_DIR = path.join(__dirname, 'uploads');
const OUTPUT_DIR = path.join(__dirname, 'output');

// Ensure upload and output directories exist
if (!fs.existsSync(UPLOAD_DIR)) {
    fs.mkdirSync(UPLOAD_DIR);
}
if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR);
}

// Set up multer for file uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, UPLOAD_DIR);
    },
    filename: (req, file, cb) => {
        const sanitizedFilename = path.basename(file.originalname);
        cb(null, sanitizedFilename);
    }
});
const upload = multer({ storage: storage });

// Endpoint to extract a frame from the video
app.post('/extract', upload.single('video'), (req, res) => {
    const videoFileName = req.file.filename;
    const frameNumber = parseInt(req.body.frameNumber, 10);

    // Validate frame number
    if (isNaN(frameNumber) || frameNumber < 0) {
        return res.status(400).json({ error: 'Invalid frame number.' });
    }

    const outputImagePath = path.join(OUTPUT_DIR, `frame_${frameNumber}.png`);

    // Construct the ffmpeg command
    const ffmpegCommand = `ffmpeg -i ${path.join(UPLOAD_DIR, videoFileName)} -vf "select=eq(n\\,${frameNumber})" -vframes 1 ${outputImagePath}`;

    // Execute the ffmpeg command
    exec(ffmpegCommand, (error) => {
        if (error) {
            return res.status(404).json({ error: `Frame at index ${frameNumber} could not be found.` });
        }

        // Send the extracted image
        res.sendFile(outputImagePath, (err) => {
            if (err) {
                return res.status(404).json({ error: 'Image not found.' });
            }
            // Optionally, clean up the output image after sending
            fs.unlinkSync(outputImagePath);
        });
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});