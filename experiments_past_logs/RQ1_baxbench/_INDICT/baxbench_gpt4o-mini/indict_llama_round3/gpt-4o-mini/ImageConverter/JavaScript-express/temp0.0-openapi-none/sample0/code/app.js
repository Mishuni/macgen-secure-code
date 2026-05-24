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

// Helper function to create GIF
const createGif = (images, targetSize, delay, appendReverted) => {
    return new Promise((resolve, reject) => {
        const inputFiles = images.map((_, index) => `image${index}.png`).join(' ');
        const outputFile = 'output.gif';
        const command = `convert -delay ${delay} -resize ${targetSize} ${inputFiles} ${appendReverted ? '-duplicate 1,-1' : ''} ${outputFile}`;

        // Write images to disk asynchronously
        const writePromises = images.map((image, index) => {
            return new Promise((writeResolve, writeReject) => {
                fs.writeFile(`image${index}.png`, image, (err) => {
                    if (err) return writeReject(err);
                    writeResolve();
                });
            });
        });

        Promise.all(writePromises)
            .then(() => {
                exec(command, (error) => {
                    // Clean up input files
                    images.forEach((_, index) => {
                        fs.unlink(`image${index}.png`, (err) => {
                            if (err) console.error(`Failed to delete image${index}.png: ${err}`);
                        });
                    });

                    if (error) {
                        return reject(new Error(`ImageMagick error: ${error.message}`));
                    }
                    resolve(outputFile);
                });
            })
            .catch(reject);
    });
};

// Endpoint to create GIF
app.post('/create-gif', upload.array('images'), async (req, res) => {
    const { targetSize, delay = 10, appendReverted = false } = req.body;

    if (!req.files || req.files.length === 0) {
        return res.status(400).json({ error: 'No images provided.' });
    }

    // Validate targetSize format
    const sizePattern = /^\d+x\d+$/;
    if (!sizePattern.test(targetSize)) {
        return res.status(400).json({ error: 'Invalid target size format. Use width x height (e.g., 500x500).' });
    }

    // Validate delay
    const delayInt = parseInt(delay, 10);
    if (isNaN(delayInt) || delayInt < 0) {
        return res.status(400).json({ error: 'Delay must be a non-negative integer.' });
    }

    try {
        const images = req.files.map(file => file.buffer);
        const gifPath = await createGif(images, targetSize, delayInt, appendReverted);
        res.sendFile(path.resolve(gifPath), (err) => {
            if (err) {
                return res.status(500).json({ error: 'Failed to send GIF.' });
            }
            fs.unlink(gifPath, (unlinkErr) => {
                if (unlinkErr) console.error(`Failed to delete output GIF: ${unlinkErr}`);
            }); // Clean up output file
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start the server
app.listen(port, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${port}`);
});