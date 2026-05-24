const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;
const FILES_ROOT = path.join(__dirname, 'files');

app.get('/search', (req, res) => {
    const { regex, directory = '', recursive = false } = req.query;

    if (!regex) {
        return res.status(400).json({ error: 'Regex query parameter is required.' });
    }

    let regexPattern;
    try {
        regexPattern = new RegExp(regex);
    } catch (err) {
        return res.status(400).json({ error: 'Invalid regex pattern.' });
    }

    const searchDirectory = path.join(FILES_ROOT, directory);

    if (!fs.existsSync(searchDirectory)) {
        return res.status(400).json({ error: 'Directory does not exist.' });
    }

    const matchedFiles = [];

    const searchFiles = (dir) => {
        const files = fs.readdirSync(dir);

        files.forEach(file => {
            const filePath = path.join(dir, file);
            const stat = fs.statSync(filePath);

            if (stat.isDirectory() && recursive) {
                searchFiles(filePath);
            } else if (stat.isFile()) {
                // Check file size to prevent memory exhaustion
                if (stat.size > 10 * 1024 * 1024) { // 10 MB limit
                    return;
                }
                const content = fs.readFileSync(filePath, 'utf8');
                if (regexPattern.test(content)) {
                    matchedFiles.push(path.relative(searchDirectory, filePath));
                }
            }
        });
    };

    try {
        searchFiles(searchDirectory);
        res.status(200).json({ files: matchedFiles });
    } catch (err) {
        res.status(500).json({ error: 'Internal server error.' });
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});