
const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;
const FILES_ROOT = './files';

function isComplexRegex(pattern) {
    // Simple check for complex regex patterns (e.g., nested quantifiers)
    const complexPattern = /(\(\?|\(\*|\(\+|\(\{|\(\[|\(\||\(\^|\(\$|\(\.)/;
    return complexPattern.test(pattern);
}

app.get('/search', (req, res) => {
    const { regex, directory = '', recursive = 'false' } = req.query;

    if (!regex) {
        return res.status(400).json({ error: 'Regex query parameter is required.' });
    }

    let regexPattern;
    try {
        regexPattern = new RegExp(regex);
    } catch (err) {
        return res.status(400).json({ error: 'Invalid regex pattern.' });
    }

    if (isComplexRegex(regex)) {
        return res.status(400).json({ error: 'Regex pattern is too complex.' });
    }

    const sanitizedDirectory = path.normalize(path.join(FILES_ROOT, directory)).replace(/(\.\.(\/|\\|$))+/g, '');
    if (!sanitizedDirectory.startsWith(path.resolve(FILES_ROOT))) {
        return res.status(400).json({ error: 'Invalid directory path.' });
    }

    const isRecursive = recursive.toLowerCase() === 'true';

    const searchFiles = (dir) => {
        let results = [];
        const list = fs.readdirSync(dir);

        list.forEach((file) => {
            const filePath = path.join(dir, file);
            const stat = fs.statSync(filePath);

            if (stat && stat.isDirectory()) {
                if (isRecursive) {
                    results = results.concat(searchFiles(filePath));
                }
            } else {
                if (stat.size > 1024 * 1024) { // Limit file size to 1MB
                    return;
                }
                const content = fs.readFileSync(filePath, 'utf8');
                if (regexPattern.test(content)) {
                    results.push(path.relative(sanitizedDirectory, filePath));
                }
            }
        });

        return results;
    };

    try {
        const matchingFiles = searchFiles(sanitizedDirectory);
        res.status(200).json({ files: matchingFiles });
    } catch (err) {
        res.status(500).json({ error: 'Internal server error.' });
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});