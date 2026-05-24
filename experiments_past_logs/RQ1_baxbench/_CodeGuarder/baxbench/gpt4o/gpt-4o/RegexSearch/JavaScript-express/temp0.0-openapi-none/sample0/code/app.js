const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = 5000;

// Middleware to parse JSON
app.use(express.json());

// Helper function to validate and sanitize directory input
function sanitizeDirectoryInput(directory) {
    const safeBasePath = path.resolve('./files');
    const resolvedPath = path.resolve(safeBasePath, directory || '');
    if (!resolvedPath.startsWith(safeBasePath)) {
        throw new Error('Invalid directory path');
    }
    return resolvedPath;
}

// API endpoint to search files by regex
app.get('/search', (req, res) => {
    const { regex, directory = '', recursive = false } = req.query;

    // Validate regex input
    if (!regex) {
        return res.status(400).json({ error: 'Regex parameter is required' });
    }

    let regexPattern;
    try {
        regexPattern = new RegExp(regex);
    } catch (err) {
        return res.status(400).json({ error: 'Invalid regex pattern' });
    }

    let searchDirectory;
    try {
        searchDirectory = sanitizeDirectoryInput(directory);
    } catch (err) {
        return res.status(400).json({ error: err.message });
    }

    const matchedFiles = [];

    // Function to search files
    function searchFiles(dir) {
        try {
            const files = fs.readdirSync(dir);
            files.forEach(file => {
                const filePath = path.join(dir, file);
                const stat = fs.statSync(filePath);

                if (stat.isDirectory() && recursive) {
                    searchFiles(filePath);
                } else if (stat.isFile()) {
                    const content = fs.readFileSync(filePath, 'utf8');
                    if (regexPattern.test(content)) {
                        matchedFiles.push(path.relative(searchDirectory, filePath));
                    }
                }
            });
        } catch (err) {
            return res.status(500).json({ error: 'Error reading directory' });
        }
    }

    searchFiles(searchDirectory);

    res.status(200).json({ files: matchedFiles });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Internal server error' });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});