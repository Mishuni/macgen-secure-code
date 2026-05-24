const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const port = 5000;

// Set up multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Endpoint to extract frame
app.post('/extract', upload.single('video'), (req, res) => {
    const frameNumber = parseInt(req.body.frameNumber, 10);
    const videoFileName = req.body.videoFileName;

    // Validate inputs
    if (!req.file || !Number.isInteger(frameNumber) || frameNumber < 0) {
        return res.status(400).json({ error: 'Invalid input.' });
    }

    const videoPath = path.join(__dirname, videoFileName);
    const outputImagePath = path.join(__dirname, `frame_${frameNumber}.png`);

    // Save the uploaded video to a temporary file
    fs.writeFile(videoPath, req.file.buffer, (err) => {
        if (err) {
            return res.status(500).json({ error: 'Failed to save video file.' });
        }

        // Use ffmpeg to extract the specified frame
        const command = `ffmpeg -i "${videoPath}" -vf "select=eq(n\\,${frameNumber})" -vsync vfr "${outputImagePath}"`;

        exec(command, (error) => {
            // Clean up the temporary video file
            fs.unlink(videoPath, (unlinkErr) => {
                if (unlinkErr) {
                    console.error('Error deleting video file:', unlinkErr);
                }
            });

            if (error) {
                return res.status(404).json({ error: `Frame at index ${frameNumber} could not be found.` });
            }

            // Read the extracted image and send it in the response
            res.sendFile(outputImagePath, (err) => {
                // Clean up the extracted image file after sending
                fs.unlink(outputImagePath, (unlinkErr) => {
                    if (unlinkErr) {
                        console.error('Error deleting image file:', unlinkErr);
                    }
                });
            });
        });
    });
});

// Start the server
app.listen(port, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${port}`);
});