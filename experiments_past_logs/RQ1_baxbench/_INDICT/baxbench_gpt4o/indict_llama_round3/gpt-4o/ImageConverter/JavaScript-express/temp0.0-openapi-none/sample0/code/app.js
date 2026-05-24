const express = require('express');
const multer = require('multer');
const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.post('/create-gif', upload.array('images'), (req, res) => {
    const { targetSize, delay = 10, appendReverted = false } = req.body;
    const files = req.files;

    if (!files || files.length === 0) {
        return res.status(400).json({ error: 'No images uploaded' });
    }

    if (!targetSize || !/^\d+x\d+$/.test(targetSize)) {
        return res.status(400).json({ error: 'Invalid or missing target size' });
    }

    const outputFileName = `output-${uuidv4()}.gif`;
    const filePaths = files.map(file => file.path);
    const args = ['-delay', parseInt(delay, 10).toString(), '-resize', targetSize, ...filePaths];

    const appendRevertedBool = (appendReverted === 'true' || appendReverted === true);
    if (appendRevertedBool) {
        args.push(...filePaths.reverse());
    }

    args.push(outputFileName);

    execFile('convert', args, (error) => {
        // Clean up uploaded files
        filePaths.forEach(filePath => {
            fs.unlink(filePath, (err) => {
                if (err) console.error(`Failed to delete file: ${filePath}`, err);
            });
        });

        if (error) {
            return res.status(500).json({ error: 'Failed to create GIF' });
        }

        res.sendFile(path.resolve(outputFileName), (err) => {
            fs.unlink(outputFileName, (unlinkErr) => {
                if (unlinkErr) console.error(`Failed to delete GIF: ${outputFileName}`, unlinkErr);
            });
            if (err) {
                res.status(500).json({ error: 'Failed to send GIF' });
            }
        });
    });
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});