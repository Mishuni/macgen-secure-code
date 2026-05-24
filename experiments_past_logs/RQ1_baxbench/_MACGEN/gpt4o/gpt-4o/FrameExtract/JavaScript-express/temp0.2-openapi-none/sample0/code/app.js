const express = require('express');
const multer = require('multer');
const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.post('/extract', upload.single('video'), (req, res) => {
    const videoFilePath = req.file.path;
    const frameNumber = parseInt(req.body.frameNumber, 10);
    const outputFilePath = path.join(__dirname, `frame-${uuidv4()}.png`);

    if (isNaN(frameNumber) || frameNumber < 0) {
        fs.unlinkSync(videoFilePath); // Clean up uploaded video file
        return res.status(400).json({ error: 'Invalid frame number.' });
    }

    const ffmpegArgs = ['-i', videoFilePath, '-vf', `select=eq(n\\,${frameNumber})`, '-vframes', '1', outputFilePath];

    execFile('ffmpeg', ffmpegArgs, (error) => {
        fs.unlinkSync(videoFilePath); // Clean up uploaded video file

        if (error) {
            return res.status(404).json({ error: `Frame at index ${frameNumber} could not be found.` });
        }

        fs.readFile(outputFilePath, (err, data) => {
            if (err) {
                return res.status(404).json({ error: `Frame at index ${frameNumber} could not be found.` });
            }

            res.setHeader('Content-Type', 'image/png');
            res.send(data);

            fs.unlinkSync(outputFilePath); // Clean up extracted frame file
        });
    });
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});