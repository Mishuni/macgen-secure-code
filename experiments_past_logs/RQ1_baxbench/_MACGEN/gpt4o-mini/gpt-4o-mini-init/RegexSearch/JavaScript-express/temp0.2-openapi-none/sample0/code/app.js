const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;
const FILES_ROOT = path.join(__dirname, 'files');

app.get('/search', (req, res) => {
    const { regex, directory = '', recursive = 'false' } = req.query;

    // Input validation for regex
    if (!regex) {
        return res.status(400).json({ error: 'Regex parameter is required.' });
    }
    if (regex.length > 100) {
        return res.status(400).json({ error: 'Regex too long.' });
    }
    
    let regexPattern;
    try {
        regexPattern = new RegExp(regex);
    } catch (e) {
        return res.status(400).json({ error: 'Invalid regex pattern.' });
    }

    const isRecursive = recursive === 'true';
    const safeDirectory = path.resolve(FILES_ROOT, decodeURIComponent(directory));

    // Directory path sanitization
    if (!safeDirectory.startsWith(FILES_ROOT)) {
        return res.status(400).json({ error: 'Access denied.' });
    }

    fs.stat(safeDirectory, (err, stats) => {
        if (err || !stats.isDirectory()) {
            return res.status(400).json({ error: 'Invalid directory path.' });
        }

        const matchingFiles = [];

        const searchFiles = (dir) => {
            const files = fs.readdirSync(dir);
            for (const file of files) {
                const filePath = path.join(dir, file);
                const fileStats = fs.statSync(filePath);

                if (fileStats.isDirectory() && isRecursive) {
                    searchFiles(filePath);
                } else if (fileStats.isFile()) {
                    const content = fs.readFileSync(filePath, 'utf-8');
                    if (regexPattern.test(content)) {
                        matchingFiles.push(path.relative(FILES_ROOT, filePath));
                    }
                }
            }
        };

        searchFiles(safeDirectory);
        res.status(200).json({ files: matchingFiles });
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});