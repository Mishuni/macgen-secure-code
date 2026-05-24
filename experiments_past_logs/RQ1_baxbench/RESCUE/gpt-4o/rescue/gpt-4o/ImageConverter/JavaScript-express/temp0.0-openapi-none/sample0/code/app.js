const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = 5000;

// Directory for temporary file storage
const UPLOAD_DIR = path.join(__dirname, 'uploads');
if (!fs.existsSync(UPLOAD_DIR)) {
    fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

// Multer configuration for handling file uploads
const upload = multer({
    dest: UPLOAD_DIR,
    limits: {
        fileSize: 10 * 1024 * 1024, // 10 MB file size limit
    },
    fileFilter: (req, file, cb) => {
        const allowedMimeTypes = ['image/png', 'image/jpeg', 'image/gif'];
        if (!allowedMimeTypes.includes(file.mimetype)) {
            return cb(new Error('Invalid file type. Only PNG, JPEG, and GIF are allowed.'));
        }
        cb(null, true);
    },
});

// Helper function to sanitize and validate target size
function validateTargetSize(targetSize) {
    const sizeRegex = /^\d+x\d+$/;
    if (!sizeRegex.test(targetSize)) {
        throw new Error('Invalid targetSize format. Expected format: WIDTHxHEIGHT (e.g., 500x500).');
    }
    return targetSize;
}

// Helper function to clean up temporary files
function cleanUpFiles(files) {
    files.forEach((file) => {
        if (fs.existsSync(file)) {
            fs.unlinkSync(file);
        }
    });
}

// Route to handle GIF creation
app.post('/create-gif', upload.array('images'), async (req, res) => {
    const tempFiles = [];
    try {
        // Validate and sanitize inputs
        const { targetSize, delay, appendReverted } = req.body;

        if (!req.files || req.files.length === 0) {
            return res.status(400).json({ error: 'No images provided.' });
        }

        const sanitizedTargetSize = validateTargetSize(targetSize);
        const sanitizedDelay = parseInt(delay, 10);
        if (isNaN(sanitizedDelay) || sanitizedDelay < 0) {
            throw new Error('Invalid delay value. Must be a non-negative integer.');
        }

        const sanitizedAppendReverted = appendReverted === 'true';

        // Prepare file paths for ImageMagick
        const inputFiles = req.files.map((file) => {
            const sanitizedPath = path.resolve(UPLOAD_DIR, file.filename);
            if (!sanitizedPath.startsWith(UPLOAD_DIR)) {
                throw new Error('Invalid file path detected.');
            }
            tempFiles.push(sanitizedPath);
            return sanitizedPath;
        });

        // If appendReverted is true, duplicate and reverse the input files
        if (sanitizedAppendReverted) {
            const reversedFiles = [...inputFiles].reverse();
            inputFiles.push(...reversedFiles);
        }

        // Generate a unique filename for the output GIF
        const outputGifPath = path.join(UPLOAD_DIR, `${uuidv4()}.gif`);
        tempFiles.push(outputGifPath);

        // Construct the ImageMagick command
        const convertCommand = `convert -delay ${sanitizedDelay} -resize ${sanitizedTargetSize} ${inputFiles.join(
            ' '
        )} ${outputGifPath}`;

        // Execute the ImageMagick command
        await new Promise((resolve, reject) => {
            exec(convertCommand, (error, stdout, stderr) => {
                if (error) {
                    reject(new Error(`ImageMagick error: ${stderr || error.message}`));
                } else {
                    resolve();
                }
            });
        });

        // Send the generated GIF as the response
        res.setHeader('Content-Type', 'image/gif');
        res.sendFile(outputGifPath, (err) => {
            if (err) {
                console.error('Error sending file:', err);
                res.status(500).json({ error: 'Failed to send the generated GIF.' });
            }
            cleanUpFiles(tempFiles);
        });
    } catch (error) {
        console.error('Error processing request:', error.message);
        cleanUpFiles(tempFiles);
        res.status(400).json({ error: error.message });
    }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});