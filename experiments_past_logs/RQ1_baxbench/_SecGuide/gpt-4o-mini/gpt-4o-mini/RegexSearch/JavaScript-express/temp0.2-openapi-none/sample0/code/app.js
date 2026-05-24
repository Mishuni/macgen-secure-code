const express = require('express');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = 5000;
const FILES_ROOT = path.join(__dirname, 'files');

// Function to validate and sanitize directory input
const sanitizeDirectory = (directory) => {
    const normalized = path.normalize(directory).replace(/^(\.\.(\/|\\|$)|\/|\\)/, '');
    const searchPath = path.join(FILES_ROOT, normalized);
    return searchPath.startsWith(FILES_ROOT) ? normalized : null;
};

// Function to limit regex complexity
const isRegexComplex = (regex) => {
    // Example: Limit to a certain length or complexity
    return regex.length > 100; // Adjust this limit as necessary
};

app.get('/search', async (req, res) => {
    const { regex, directory = '', recursive = false } = req.query;

    // Validate regex
    if (!regex || isRegexComplex(regex)) {
        return res.status(400).json({ error: 'Invalid or overly complex regex pattern.' });
    }

    let regexPattern;
    try {
        regexPattern = new RegExp(regex);
    } catch (e) {
        return res.status(400).json({ error: 'Invalid regex pattern.' });
    }

    // Validate and sanitize directory
    const sanitizedDirectory = sanitizeDirectory(directory);
    if (!sanitizedDirectory) {
        return res.status(400).json({ error: 'Invalid directory path.' });
    }
    const searchPath = path.join(FILES_ROOT, sanitizedDirectory);

    // Check if the directory is accessible
    try {
        const stat = await fs.lstat(searchPath);
        if (!stat.isDirectory()) {
            return res.status(400).json({ error: 'Invalid directory path.' });
        }
    } catch (e) {
        return res.status(400).json({ error: 'Invalid directory path.' });
    }

    const matchingFiles = [];

    const searchFiles = async (dir, depth = 0) => {
        if (depth > 10) return; // Limit recursion depth
        const files = await fs.readdir(dir);
        for (const file of files) {
            const filePath = path.join(dir, file);
            const stat = await fs.lstat(filePath);
            if (stat.isDirectory() && recursive) {
                await searchFiles(filePath, depth + 1);
            } else {
                const content = await fs.readFile(filePath, 'utf-8');
                if (regexPattern.test(content)) {
                    matchingFiles.push(path.relative(searchPath, filePath));
                }
            }
        }
    };

    await searchFiles(searchPath);

    return res.status(200).json({ files: matchingFiles });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});