const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

const DATA_DIR = path.resolve(__dirname, 'data');

// Helper function to sanitize and validate directory paths
function sanitizePath(inputPath) {
    const resolvedPath = path.resolve(DATA_DIR, inputPath || '');
    if (!resolvedPath.startsWith(DATA_DIR)) {
        throw new Error('Invalid directory path');
    }
    return resolvedPath;
}

// Helper function to search for files by content
function searchFilesByContent(directory, searchContent) {
    const result = [];
    const files = fs.readdirSync(directory, { withFileTypes: true });

    for (const file of files) {
        const filePath = path.join(directory, file.name);
        if (file.isDirectory()) {
            result.push(...searchFilesByContent(filePath, searchContent));
        } else if (file.isFile()) {
            try {
                const fileContent = fs.readFileSync(filePath, 'utf8');
                if (fileContent.includes(searchContent)) {
                    result.push(filePath);
                }
            } catch (err) {
                console.error(`Error reading file: ${filePath}`, err);
            }
        }
    }
    return result;
}

// Helper function to search for files by filename
function searchFilesByName(directory, searchFilename) {
    const result = [];
    const files = fs.readdirSync(directory, { withFileTypes: true });

    for (const file of files) {
        const filePath = path.join(directory, file.name);
        if (file.isDirectory()) {
            result.push(...searchFilesByName(filePath, searchFilename));
        } else if (file.isFile() && file.name === searchFilename) {
            result.push(filePath);
        }
    }
    return result;
}

// POST /search endpoint
app.post('/search', (req, res) => {
    const { search_content, search_filename, search_dir } = req.body;

    try {
        // Validate input types
        if (search_content && typeof search_content !== 'string') {
            return res.status(400).json({ error: 'Invalid search_content' });
        }
        if (search_filename && typeof search_filename !== 'string') {
            return res.status(400).json({ error: 'Invalid search_filename' });
        }
        if (search_dir && typeof search_dir !== 'string') {
            return res.status(400).json({ error: 'Invalid search_dir' });
        }

        // Sanitize and resolve the search directory
        const directory = sanitizePath(search_dir);

        let files = [];
        if (search_content) {
            files = searchFilesByContent(directory, search_content);
        }
        if (search_filename) {
            files = files.concat(searchFilesByName(directory, search_filename));
        }

        // Remove duplicates and return the result
        files = [...new Set(files)];
        res.status(200).json({ files });
    } catch (err) {
        console.error('Error processing request:', err);
        res.status(400).json({ error: 'Invalid input or server error' });
    }
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});