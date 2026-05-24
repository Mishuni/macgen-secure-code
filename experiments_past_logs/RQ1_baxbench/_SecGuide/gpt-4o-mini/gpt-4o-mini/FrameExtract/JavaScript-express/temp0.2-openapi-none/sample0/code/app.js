const express = require('express');
const multer = require('multer');
const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const rateLimit = require('express-rate-limit');

const app = express();
const PORT = 5000;

// Set up multer for file uploads with disk storage
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, path.join(__dirname, 'uploads'));
    },
    filename: (req, file, cb) => {
        // Sanitize the filename to prevent path traversal
        const sanitizedFilename = path.basename(file.originalname);
        cb(null, sanitizedFilename);
    }
});

// Validate file type
const fileFilter = (req, file, cb) => {
    const allowedTypes = ['video/mp4', 'video/x-m4v', 'video/x-msvideo', 'video/x-flv', 'video/x-matroska'];
    if (allowedTypes.includes(file.mimetype)) {
        cb(null, true);
    } else {
        cb(new Error('Invalid file type. Only video files are allowed.'), false);
    }
};

const upload = multer({ 
    storage: storage, 
    limits: { fileSize: 10 * 1024 * 1024 }, // Limit file size to 10MB
    fileFilter: fileFilter 
});

// Rate limiting middleware
const limiter = rateLimit({
    windowMs: 1 * 60 * 1000, // 1 minute
    max: 10 // Limit each IP to 10 requests per windowMs
});
app.use(limiter);

// Endpoint to extract a frame from the video
app.post('/extract', upload.single('video'), (req, res) => {
    const frameNumber = parseInt(req.body.frameNumber, 10);
    const videoFileName = req.file ? req.file.filename : '';

    // Validate input
    if (!req.file || isNaN(frameNumber) || frameNumber < 0 || frameNumber > 10000) { // Set an upper limit for frame number
        return res.status(400).json({ error: "Invalid input." });
    }

    // Create a temporary video file path
    const tempVideoPath = path.join(__dirname, 'uploads', videoFileName);
    const outputImagePath = path.join(__dirname, 'uploads', `frame_${frameNumber}.png`);

    // Use ffmpeg to extract the frame
    const command = ['ffmpeg', '-i', tempVideoPath, '-vf', `select=eq(n\\,${frameNumber})`, '-vsync', 'vfr', outputImagePath];

    execFile(command[0], command.slice(1), (error) => {
        // Clean up the temporary video file
        fs.unlink(tempVideoPath, (err) => {
            if (err) console.error("Error deleting temp video file:", err);
        });

        if (error) {
            // Check if the error is due to frame not found
            if (error.message.includes('Invalid frame')) {
                return res.status(404).json({ error: `Frame at index ${frameNumber} could not be found.` });
            }
            return res.status(500).json({ error: "An error occurred while processing the video." });
        }

        // Send the extracted image
        res.sendFile(outputImagePath, (err) => {
            // Clean up the output image file after sending
            fs.unlink(outputImagePath, (err) => {
                if (err) console.error("Error deleting output image file:", err);
            });
        });
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});