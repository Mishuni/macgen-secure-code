const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.post('/create-gif', upload.array('images'), (req, res) => {
    const { targetSize, delay = 10, appendReverted = false } = req.body;
    const images = req.files;

    // Validate input parameters
    if (!images || images.length === 0) {
        return res.status(400).json({ error: 'No images uploaded' });
    }

    if (!targetSize || !/^\d+x\d+$/.test(targetSize)) {
        return res.status(400).json({ error: 'Invalid target size format' });
    }

    const delayInt = parseInt(delay, 10);
    if (isNaN(delayInt) || delayInt < 10 || delayInt > 1000) {
        return res.status(400).json({ error: 'Invalid delay value' });
    }

    const appendRevertedBool = appendReverted === 'true';

    const imagePaths = images.map(file => file.path);
    let command = `convert -delay ${delayInt} ${imagePaths.join(' ')} -resize ${targetSize}`;

    if (appendRevertedBool) {
        const reversedPaths = [...imagePaths].reverse();
        command += ` ${reversedPaths.join(' ')}`;
    }

    const outputFileName = `output-${uuidv4()}.gif`;
    const outputPath = path.join(__dirname, outputFileName);

    command += ` ${outputPath}`;

    exec(command, (error) => {
        imagePaths.forEach(filePath => fs.unlinkSync(filePath)); // Clean up uploaded files

        if (error) {
            return res.status(500).json({ error: 'Failed to create GIF' });
        }

        res.sendFile(outputPath, (err) => {
            fs.unlinkSync(outputPath); // Clean up output file
            if (err) {
                res.status(500).json({ error: 'Failed to send GIF' });
            }
        });
    });
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});