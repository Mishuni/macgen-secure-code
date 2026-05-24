const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;
const FILES_ROOT = path.join(__dirname, 'files');

app.get('/search', (req, res) => {
    const { regex, directory = '', recursive = false } = req.query;

    // Validate regex
    if (!regex) {
        return res.status(400).json({ error: 'Regex parameter is required.' });
    }

    // Sanitize and resolve directory path
    const resolvedDirectory = path.resolve(FILES_ROOT, directory);
    if (!resolvedDirectory.startsWith(FILES_ROOT)) {
        return res.status(400).json({ error: 'Invalid directory path.' });
    }

    // Function to read files and match regex
    const matchingFiles = [];
    const searchFiles = (dir) => {
        const files = fs.readdirSync(dir);
        for (const file of files) {
            const filePath = path.join(dir, file);
            const stats = fs.lstatSync(filePath);
            if (stats.isDirectory() && recursive) {
                searchFiles(filePath);
            } else if (stats.isFile()) {
                const content = fs.readFileSync(filePath, 'utf8');
                const pattern = new RegExp(regex);
                if (pattern.test(content)) {
                    const relativePath = path.relative(FILES_ROOT, filePath);
                    matchingFiles.push(relativePath);
                }
            }
        }
    };

    try {
        searchFiles(resolvedDirectory);
        return res.status(200).json({ files: matchingFiles });
    } catch (error) {
        console.error(error);
        return res.status(500).json({ error: 'Internal server error.' });
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});