const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;
const FILES_ROOT = path.join(__dirname, 'files');

app.get('/search', (req, res) => {
    const regexPattern = req.query.regex;
    const directory = req.query.directory || '';
    const recursive = req.query.recursive === 'true';

    // Validate regex pattern
    let regex;
    try {
        regex = new RegExp(regexPattern);
    } catch (e) {
        return res.status(400).json({ error: 'Invalid regex pattern.' });
    }

    // Construct the search directory path
    const searchDir = path.join(FILES_ROOT, directory);

    // Validate directory
    if (!fs.existsSync(searchDir) || !fs.lstatSync(searchDir).isDirectory()) {
        return res.status(400).json({ error: 'Invalid or inaccessible directory.' });
    }

    const matchingFiles = [];

    // Function to search files
    const searchFiles = (dir) => {
        const files = fs.readdirSync(dir);
        for (const file of files) {
            const filePath = path.join(dir, file);
            if (fs.lstatSync(filePath).isDirectory()) {
                if (recursive) {
                    searchFiles(filePath); // Recurse into subdirectory
                }
            } else {
                const content = fs.readFileSync(filePath, 'utf8');
                if (regex.test(content)) {
                    // Store the relative path
                    matchingFiles.push(path.relative(FILES_ROOT, filePath));
                }
            }
        }
    };

    // Start searching
    searchFiles(searchDir);

    // Return the matching files
    res.status(200).json({ files: matchingFiles });
});

app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});