const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

const app = express();
const port = 5000;

// Set up multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Helper function to create a temporary file
function createTempFile(content, extension) {
    const tempFilePath = path.join(os.tmpdir(), `${Date.now()}.${extension}`);
    fs.writeFileSync(tempFilePath, content);
    return tempFilePath;
}

// Endpoint to create GIF
app.post('/create-gif', upload.array('images'), (req, res) => {
    const { targetSize, delay, appendReverted } = req.body;
    const images = req.files;

    if (!images || images.length === 0) {
        return res.status(400).json({ error: 'No images provided.' });
    }

    // Create temporary files for images
    const tempImagePaths = images.map(file => createTempFile(file.buffer, path.extname(file.originalname).slice(1)));

    // Construct the convert command
    let command = `convert -delay ${delay} -resize ${targetSize} ${tempImagePaths.join(' ')} output.gif`;
    if (appendReverted === 'true') {
        command += ` -reverse output.gif`;
    }

    // Execute the command
    exec(command, (error) => {
        // Clean up temporary files
        tempImagePaths.forEach(filePath => fs.unlinkSync(filePath));

        if (error) {
            return res.status(500).json({ error: 'Failed to create GIF.' });
        }

        // Send the GIF back to the client
        res.sendFile(path.join(__dirname, 'output.gif'), (err) => {
            if (err) {
                return res.status(500).json({ error: 'Failed to send GIF.' });
            }
            // Clean up the output GIF after sending
            fs.unlinkSync(path.join(__dirname, 'output.gif'));
        });
    });
});

// Start the server
app.listen(port, () => {
    console.log(`Server running at http://0.0.0.0:${port}`);
});