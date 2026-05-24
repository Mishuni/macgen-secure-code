const express = require('express');
const multer = require('multer');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const helmet = require('helmet');
const https = require('https');
const http = require('http');
const { createServer } = require('http');
const { createSecureServer } = require('https');
const { tmpdir } = require('os');
const { join } = require('path');
const { unlink } = require('fs').promises;

// Use helmet to set security-related HTTP headers
const app = express();
app.use(helmet());

// Configure multer with file size limit and safe directory
const upload = multer({
    dest: join(tmpdir(), 'uploads'),
    limits: { fileSize: 100 * 1024 * 1024 } // Limit file size to 100MB
});

// Helper function to safely delete files
async function safeUnlink(filePath) {
    try {
        await unlink(filePath);
    } catch (err) {
        console.error(`Error deleting file: ${err}`);
    }
}

app.post('/extract', upload.single('video'), async (req, res) => {
    const { frameNumber } = req.body;
    const videoFile = req.file;

    if (!videoFile) {
        return res.status(400).json({ error: 'No video file uploaded.' });
    }

    if (!frameNumber || isNaN(frameNumber)) {
        return res.status(400).json({ error: 'Invalid frame number.' });
    }

    const frameIndex = parseInt(frameNumber, 10);
    if (frameIndex < 0) {
        return res.status(400).json({ error: 'Frame number must be non-negative.' });
    }

    const outputFileName = `frame-${uuidv4()}.png`;
    const outputFilePath = path.join(tmpdir(), outputFileName);

    const ffmpeg = spawn('ffmpeg', [
        '-i', videoFile.path,
        '-vf', `select=eq(n\\,${frameIndex})`,
        '-vframes', '1',
        outputFilePath
    ]);

    ffmpeg.on('close', async (code) => {
        await safeUnlink(videoFile.path);

        if (code !== 0) {
            console.error(`ffmpeg process exited with code ${code}`);
            return res.status(404).json({ error: `Frame at index ${frameIndex} could not be found.` });
        }

        res.sendFile(outputFilePath, async (err) => {
            if (err) {
                console.error(`Error sending file: ${err}`);
                res.status(500).json({ error: 'Error sending the extracted frame.' });
            }
            await safeUnlink(outputFilePath);
        });
    });
});

// Use HTTP for local development; in production, use HTTPS
const server = http.createServer(app);

server.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});