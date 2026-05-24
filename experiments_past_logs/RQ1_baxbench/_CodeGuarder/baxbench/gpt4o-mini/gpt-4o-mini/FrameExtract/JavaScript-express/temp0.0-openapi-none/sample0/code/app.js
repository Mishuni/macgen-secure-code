const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 5000;

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        cb(null, file.originalname);
    }
});

const upload = multer({ 
    storage: storage,
    fileFilter: (req, file, cb) => {
        const ext = path.extname(file.originalname);
        const allowedExtensions = ['.mp4', '.mkv', '.avi', '.mov'];
        if (!allowedExtensions.includes(ext)) {
            return cb(new Error('Only video files are allowed!'), false);
        }
        cb(null, true);
    }
});

// Ensure uploads directory exists
if (!fs.existsSync('uploads')) {
    fs.mkdirSync('uploads');
}

app.post('/extract', upload.single('video'), (req, res) => {
    const frameNumber = parseInt(req.body.frameNumber, 10);
    const videoFilePath = path.join(__dirname, 'uploads', req.file.filename);
    const outputImagePath = path.join(__dirname, 'uploads', `frame_${frameNumber}.png`);

    if (isNaN(frameNumber) || frameNumber < 0) {
        return res.status(400).json({ error: 'Invalid frame number provided.' });
    }

    const ffmpegCommand = `ffmpeg -i "${videoFilePath}" -vf "select=eq(n\\,${frameNumber})" -vsync vfr "${outputImagePath}"`;

    exec(ffmpegCommand, (error, stdout, stderr) => {
        if (error) {
            if (stderr.includes('Invalid frame number')) {
                return res.status(404).json({ error: `Frame at index ${frameNumber} could not be found.` });
            }
            return res.status(500).json({ error: 'An error occurred while processing the video.' });
        }

        // Send the extracted image back to the client
        res.status(200).sendFile(outputImagePath, (err) => {
            if (err) {
                return res.status(500).json({ error: 'Failed to send the extracted image.' });
            }
            // Clean up the uploaded video and extracted image after sending
            fs.unlinkSync(videoFilePath);
            fs.unlinkSync(outputImagePath);
        });
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});