const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

const DATA_DIR = path.join(__dirname, 'data');

app.post('/search', (req, res) => {
    const { search_content, search_filename, search_dir } = req.body;

    if (!search_content && !search_filename) {
        return res.status(400).json({ error: 'Either search_content or search_filename must be provided.' });
    }

    const searchPath = search_dir ? path.join(DATA_DIR, path.normalize(search_dir)) : DATA_DIR;

    if (!searchPath.startsWith(DATA_DIR) || !fs.existsSync(searchPath)) {
        return res.status(400).json({ error: 'Invalid search directory.' });
    }

    const files = [];

    const searchFiles = (dir) => {
        const items = fs.readdirSync(dir);

        items.forEach(item => {
            const fullPath = path.join(dir, item);
            const stat = fs.statSync(fullPath);

            if (stat.isDirectory()) {
                searchFiles(fullPath);
            } else {
                let match = false;

                if (search_filename && item.startsWith(search_filename)) {
                    match = true;
                }

                if (search_content) {
                    const content = fs.readFileSync(fullPath, 'utf8');
                    if (content.includes(search_content)) {
                        match = true;
                    }
                }

                if (match) {
                    files.push(fullPath);
                }
            }
        });
    };

    try {
        searchFiles(searchPath);
    } catch (error) {
        return res.status(500).json({ error: 'Error reading files.' });
    }

    res.status(200).json({ files });
});

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});