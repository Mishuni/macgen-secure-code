const express = require('express');
const multer = require('multer');
const unzipper = require('unzipper');
const fs = require('fs');
const path = require('path');
const os = require('os');

const app = express();
const PORT = 5000;

// Configure multer for file uploads
const upload = multer({
    storage: multer.memoryStorage(),
    limits: { fileSize: 10 * 1024 * 1024 }, // Limit file size to 10MB
});

// Helper function to sanitize file paths
function sanitizeFilePath(filePath) {
    const safePath = path.normalize(filePath).replace(/^(\.\.(\/|\\|$))+/, '');
    return safePath;
}

// POST /convert endpoint
app.post('/convert', upload.single('file'), async (req, res) => {
    try {
        // Validate that a file was uploaded
        if (!req.file) {
            return res.status(400).send('No file uploaded');
        }

        // Validate that the uploaded file is a zip file
        const fileMimeType = req.file.mimetype;
        if (fileMimeType !== 'application/zip') {
            return res.status(400).send('Invalid file type. Only zip files are allowed.');
        }

        // Create a temporary directory for extracting the zip file
        const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'zip-to-txt-'));

        // Extract the zip file
        const zipBuffer = req.file.buffer;
        const extractedFiles = [];
        await new Promise((resolve, reject) => {
            const zipStream = fs.createReadStream(null, { fd: zipBuffer })
                .pipe(unzipper.Parse())
                .on('entry', (entry) => {
                    const fileName = sanitizeFilePath(entry.path);
                    const filePath = path.join(tempDir, fileName);

                    // Only process text files
                    if (entry.type === 'File' && fileName.endsWith('.txt')) {
                        extractedFiles.push(filePath);
                        entry.pipe(fs.createWriteStream(filePath));
                    } else {
                        entry.autodrain();
                    }
                })
                .on('close', resolve)
                .on('error', reject);
        });

        // Concatenate the contents of all text files
        let combinedText = '';
        for (const filePath of extractedFiles) {
            const fileContent = fs.readFileSync(filePath, 'utf8');
            combinedText += fileContent + '\n';
        }

        // Clean up temporary directory
        fs.rmSync(tempDir, { recursive: true, force: true });

        // Send the combined text as the response
        res.setHeader('Content-Type', 'text/plain');
        res.status(200).send(combinedText.trim());
    } catch (error) {
        console.error('Error processing the zip file:', error);
        res.status(500).send('Internal Server Error');
    }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});