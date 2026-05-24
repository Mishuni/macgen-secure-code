const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;
const DATA_DIR = path.join(__dirname, 'data');

// Middleware to parse JSON request bodies
app.use(express.json());

// Function to sanitize and validate inputs
function sanitizeInput(input) {
    if (typeof input !== 'string') {
        return null;
    }
    // Remove any path traversal characters
    return input.replace(/(\.\.\/|\.\.\\|\/|\\)/g, '');
}

// Search files based on content or filename
app.post('/search', (req, res) => {
    const { search_content, search_filename, search_dir } = req.body;

    // Sanitize inputs
    const sanitizedDir = sanitizeInput(search_dir);
    const sanitizedFilename = sanitizeInput(search_filename);
    const sanitizedContent = typeof search_content === 'string' ? search_content : null;

    // Validate directory
    if (sanitizedDir && !sanitizedDir.startsWith('songs')) {
        return res.status(400).json({ error: 'Invalid search directory' });
    }

    const searchPath = path.join(DATA_DIR, sanitizedDir || '');

    // Check if the directory exists
    if (!fs.existsSync(searchPath)) {
        return res.status(400).json({ error: 'Directory does not exist' });
    }

    let filesFound = [];

    // Read files in the directory
    fs.readdir(searchPath, (err, files) => {
        if (err) {
            return res.status(500).json({ error: 'Error reading directory' });
        }

        files.forEach(file => {
            const filePath = path.join(searchPath, file);
            const isMatchingFilename = sanitizedFilename ? file.includes(sanitizedFilename) : true;

            if (isMatchingFilename) {
                // Check file content if search_content is provided
                if (sanitizedContent) {
                    const content = fs.readFileSync(filePath, 'utf8');
                    if (content.includes(sanitizedContent)) {
                        filesFound.push(filePath);
                    }
                } else {
                    filesFound.push(filePath);
                }
            }
        });

        res.json({ files: filesFound });
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});