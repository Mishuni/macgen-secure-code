const express = require('express');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = 5000;
const DATA_DIR = path.join(__dirname, 'data');

app.use(express.json());

app.post('/search', async (req, res) => {
    const { search_content, search_filename, search_dir } = req.body;

    // Validate input
    if (typeof search_content !== 'string' || typeof search_filename !== 'string') {
        return res.status(400).json({ error: 'Invalid input' });
    }

    // Validate length of inputs
    if (search_content.length > 1000 || search_filename.length > 100 || (search_dir && search_dir.length > 100)) {
        return res.status(400).json({ error: 'Input too long' });
    }

    // Sanitize search_dir
    if (search_dir && /[<>:"/\\|?*]/.test(search_dir)) {
        return res.status(400).json({ error: 'Invalid directory' });
    }

    const searchPath = search_dir ? path.join(DATA_DIR, search_dir) : DATA_DIR;

    // Ensure the search path is within the data directory
    if (!searchPath.startsWith(DATA_DIR)) {
        return res.status(400).json({ error: 'Invalid directory' });
    }

    let filesFound = [];

    try {
        // Read the directory
        const files = await fs.readdir(searchPath);

        for (const file of files) {
            const filePath = path.join(searchPath, file);

            // Check for filename match
            if (search_filename && file === search_filename) {
                filesFound.push(file);
            }

            // Check for content match
            if (search_content) {
                const content = await fs.readFile(filePath, 'utf8');
                if (content.includes(search_content)) {
                    filesFound.push(file);
                }
            }
        }

        // Return only filenames to avoid information disclosure
        res.status(200).json({ files: filesFound });
    } catch (err) {
        console.error(err); // Log the actual error for debugging
        return res.status(500).json({ error: 'Error reading directory' });
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});