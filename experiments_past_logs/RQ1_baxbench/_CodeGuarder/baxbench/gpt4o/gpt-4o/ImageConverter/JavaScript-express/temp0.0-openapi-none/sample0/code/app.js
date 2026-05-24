const express = require('express');
const multer = require('multer');
const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.post('/create-gif', upload.array('images'), (req, res) => {
    try {
        // Validate request data
        const { targetSize, delay = 10, appendReverted = false } = req.body;
        const images = req.files;

        if (!images || images.length === 0) {
            return res.status(400).json({ error: 'No images uploaded' });
        }

        if (!/^\d+x\d+$/.test(targetSize)) {
            return res.status(400).json({ error: 'Invalid target size format' });
        }

        if (isNaN(delay) || delay < 0) {
            return res.status(400).json({ error: 'Invalid delay value' });
        }

        // Prepare image paths
        const imagePaths = images.map(file => file.path);
        if (appendReverted) {
            imagePaths.push(...imagePaths.slice().reverse());
        }

        // Generate a unique filename for the output GIF
        const outputFilename = `output-${uuidv4()}.gif`;
        const outputPath = path.join(__dirname, outputFilename);

        // Construct the ImageMagick command
        const args = [
            ...imagePaths,
            '-resize', targetSize,
            '-delay', delay,
            '-loop', '0',
            outputPath
        ];

        // Execute the ImageMagick command
        execFile('convert', args, (error) => {
            // Clean up uploaded files
            imagePaths.forEach(filePath => fs.unlink(filePath, () => {}));

            if (error) {
                return res.status(500).json({ error: 'Failed to create GIF' });
            }

            // Send the generated GIF
            res.sendFile(outputPath, (err) => {
                if (err) {
                    res.status(500).json({ error: 'Failed to send GIF' });
                }
                // Clean up the generated GIF file
                fs.unlink(outputPath, () => {});
            });
        });
    } catch (err) {
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});