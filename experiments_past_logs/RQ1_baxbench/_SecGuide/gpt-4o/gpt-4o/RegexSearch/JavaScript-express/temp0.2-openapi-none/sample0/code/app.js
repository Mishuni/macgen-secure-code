const express = require('express');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = 5000;
const FILES_ROOT = path.join(__dirname, 'files');

// Utility function to validate and sanitize directory input
function sanitizeDirectoryInput(directory) {
    if (directory) {
        // Use path.resolve to prevent directory traversal
        const resolvedPath = path.resolve(FILES_ROOT, directory);
        if (!resolvedPath.startsWith(FILES_ROOT)) {
            throw new Error('Invalid directory path.');
        }
        return path.relative(FILES_ROOT, resolvedPath);
    }
    return '';
}

// Function to limit regex complexity to prevent ReDoS
function isSafeRegex(pattern) {
    // Simple heuristic to limit regex complexity
    const complexityLimit = 1000;
    return pattern.length < complexityLimit && !pattern.includes('.*.*');
}

// Function to search files based on regex
async function searchFiles(directory, regex, recursive) {
    const results = [];
    const dirPath = path.join(FILES_ROOT, directory);

    async function searchInDirectory(currentPath) {
        const files = await fs.readdir(currentPath);

        for (const file of files) {
            const fullPath = path.join(currentPath, file);
            const relativePath = path.relative(FILES_ROOT, fullPath);
            const stats = await fs.stat(fullPath);

            if (stats.isDirectory()) {
                if (recursive) {
                    await searchInDirectory(fullPath);
                }
            } else {
                const content = await fs.readFile(fullPath, 'utf8');
                if (regex.test(content)) {
                    results.push(relativePath);
                }
            }
        }
    }

    await searchInDirectory(dirPath);
    return results;
}

app.get('/search', async (req, res) => {
    try {
        const { regex, directory = '', recursive = 'false' } = req.query;

        if (!regex) {
            return res.status(400).json({ error: 'Regex parameter is required.' });
        }

        // Validate and sanitize directory input
        const sanitizedDirectory = sanitizeDirectoryInput(directory);

        // Validate regex complexity
        if (!isSafeRegex(regex)) {
            return res.status(400).json({ error: 'Regex pattern is too complex.' });
        }

        // Create a RegExp object from the regex string
        let regexObj;
        try {
            regexObj = new RegExp(regex);
        } catch (e) {
            return res.status(400).json({ error: 'Invalid regex pattern.' });
        }

        // Perform the file search
        const matchingFiles = await searchFiles(sanitizedDirectory, regexObj, recursive === 'true');

        res.status(200).json({ files: matchingFiles });
    } catch (error) {
        console.error('Error during search:', error.message);
        res.status(500).json({ error: 'An internal server error occurred.' });
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});