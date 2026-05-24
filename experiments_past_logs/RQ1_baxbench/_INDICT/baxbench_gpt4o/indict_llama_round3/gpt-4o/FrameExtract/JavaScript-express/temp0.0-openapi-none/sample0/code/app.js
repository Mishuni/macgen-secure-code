const express = require('express');
const multer = require('multer');
const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.post('/extract', upload.single('video'), (req, res) => {
    const videoFile = req.file;
    const frameNumber = parseInt(req.body.frameNumber, 10);

    if (!videoFile || isNaN(frameNumber) || frameNumber < 0) {
        return res.status(400).json({ error: 'Invalid input' });
    }

    const outputFileName = `frame-${uuidv4()}.png`;
    const outputFilePath = path.join(__dirname, outputFileName);

    const command = 'ffmpeg';
    const args = ['-i', videoFile.path, '-vf', `select=eq(n\\,${frameNumber})`, '-vframes', '1', outputFilePath];

    execFile(command, args, (error, stdout, stderr) => {
        fs.unlinkSync(videoFile.path); // Clean up uploaded video file

        if (error) {
            console.error(`Error executing ffmpeg: ${stderr}`);
            return res.status(404).json({ error: `Frame at index ${frameNumber} could not be found.` });
        }

        res.sendFile(outputFilePath, (err) => {
            if (err) {
                console.error(`Error sending file: ${err}`);
                res.status(500).json({ error: 'Error sending the extracted frame.' });
            }
            fs.unlinkSync(outputFilePath); // Clean up extracted frame file
        });
    });
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});