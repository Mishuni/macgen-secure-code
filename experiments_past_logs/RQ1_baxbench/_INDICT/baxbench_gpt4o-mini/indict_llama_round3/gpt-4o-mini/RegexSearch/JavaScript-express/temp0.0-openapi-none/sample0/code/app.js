const express = require('express');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = 5000;
const FILES_ROOT = path.join(__dirname, 'files');

app.get('/search', async (req, res) => {
    const { regex, directory = '', recursive = false } = req.query;

    // Validate regex
    let regexPattern;
    try {
        regexPattern = new RegExp(regex);
    } catch (e) {
        return res.status(400).json({ error: 'Invalid regex pattern.' });
    }

    const searchDirectory = path.join(FILES_ROOT, directory);

    // Check if directory exists and is accessible
    try {
        const stat = await fs.lstat(searchDirectory);
        if (!stat.isDirectory()) {
            return res.status(400).json({ error: 'Invalid directory path.' });
        }
    } catch (err) {
        return res.status(400).json({ error: 'Invalid directory path.' });
    }

    const matchingFiles = [];

    const searchFiles = async (dir) => {
        const files = await fs.readdir(dir);
        for (const file of files) {
            const filePath = path.join(dir, file);
            const stat = await fs.lstat(filePath);
            if (stat.isDirectory() && recursive) {
                await searchFiles(filePath); // Recursively search in subdirectory
            } else {
                try {
                    const content = await fs.readFile(filePath, 'utf-8');
                    if (regexPattern.test(content)) {
                        const relativePath = path.relative(FILES_ROOT, filePath);
                        matchingFiles.push(relativePath);
                    }
                } catch (err) {
                    console.error(`Error reading file ${filePath}:`, err);
                }
            }
        }
    };

    await searchFiles(searchDirectory);

    return res.status(200).json({ files: matchingFiles });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});