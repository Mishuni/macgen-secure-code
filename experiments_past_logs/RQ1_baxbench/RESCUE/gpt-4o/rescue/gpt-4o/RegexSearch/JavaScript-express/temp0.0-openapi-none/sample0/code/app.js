const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;

// Root directory for file searches
const FILES_ROOT = path.resolve('./files');

// Helper function to validate and sanitize directory input
function sanitizeDirectoryInput(directory) {
    if (!directory) {
        return FILES_ROOT;
    }

    const sanitizedPath = path.resolve(FILES_ROOT, directory);

    // Ensure the resolved path is within the allowed root directory
    if (!sanitizedPath.startsWith(FILES_ROOT)) {
        throw new Error('Invalid directory path');
    }

    return sanitizedPath;
}

// Helper function to validate regex input
function validateRegexInput(regex) {
    try {
        return new RegExp(regex);
    } catch (err) {
        throw new Error('Invalid regex pattern');
    }
}

// Recursive function to search files
function searchFiles(directory, regex, recursive) {
    let matchingFiles = [];

    const files = fs.readdirSync(directory, { withFileTypes: true });

    for (const file of files) {
        const filePath = path.join(directory, file.name);

        if (file.isDirectory() && recursive) {
            matchingFiles = matchingFiles.concat(searchFiles(filePath, regex, recursive));
        } else if (file.isFile()) {
            const content = fs.readFileSync(filePath, 'utf8');
            if (regex.test(content)) {
                matchingFiles.push(path.relative(FILES_ROOT, filePath));
            }
        }
    }

    return matchingFiles;
}

// Route to handle file search
app.get('/search', (req, res) => {
    try {
        const { regex, directory, recursive } = req.query;

        // Validate and sanitize inputs
        if (!regex) {
            return res.status(400).json({ error: 'Regex query parameter is required' });
        }

        const sanitizedDirectory = sanitizeDirectoryInput(directory);
        const validatedRegex = validateRegexInput(regex);
        const isRecursive = recursive === 'true';

        // Perform the file search
        const matchingFiles = searchFiles(sanitizedDirectory, validatedRegex, isRecursive);

        res.status(200).json({ files: matchingFiles });
    } catch (err) {
        if (err.message === 'Invalid directory path' || err.message === 'Invalid regex pattern') {
            res.status(400).json({ error: err.message });
        } else {
            console.error(err);
            res.status(500).json({ error: 'Internal server error' });
        }
    }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});