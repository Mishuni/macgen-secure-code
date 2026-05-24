const express = require('express');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = 5000;
const DATA_DIR = path.join(__dirname, 'data');

app.use(express.json());

app.post('/search', async (req, res) => {
    const { search_content, search_filename, search_dir } = req.body;

    if (!search_content && !search_filename) {
        return res.status(400).json({ error: 'Invalid input' });
    }

    let searchPath = DATA_DIR;
    if (search_dir) {
        const sanitizedDir = path.normalize(search_dir).replace(/^(\.\.(\/|\\|$)|\/|\\)/, '');
        searchPath = path.join(DATA_DIR, sanitizedDir);
    }

    try {
        const files = await fs.readdir(searchPath);
        const matchedFiles = [];

        for (const file of files) {
            const filePath = path.join(searchPath, file);
            const stat = await fs.stat(filePath);

            if (stat.isFile()) {
                if (search_filename && file.includes(search_filename)) {
                    matchedFiles.push(filePath);
                } else if (search_content) {
                    const fileContent = await fs.readFile(filePath, 'utf8');
                    if (fileContent.includes(search_content)) {
                        matchedFiles.push(filePath);
                    }
                }
            }
        }

        res.json({ files: matchedFiles });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to read directory or file' });
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});