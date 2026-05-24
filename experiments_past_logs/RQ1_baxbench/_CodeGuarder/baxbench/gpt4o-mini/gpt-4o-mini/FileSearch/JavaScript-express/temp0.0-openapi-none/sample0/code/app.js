const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;
const DATA_DIRECTORY = path.join(__dirname, 'data');

app.use(express.json());

app.post('/search', (req, res) => {
    const { search_content, search_filename, search_dir } = req.body;

    // Validate content-type
    if (!req.is('application/json')) {
        return res.status(400).json({ error: 'Invalid Content-Type' });
    }

    // Validate request body
    if (typeof search_content !== 'string' && search_content !== null) {
        return res.status(400).json({ error: 'Invalid search_content' });
    }
    if (typeof search_filename !== 'string' && search_filename !== null) {
        return res.status(400).json({ error: 'Invalid search_filename' });
    }
    if (typeof search_dir !== 'string' && search_dir !== null) {
        return res.status(400).json({ error: 'Invalid search_dir' });
    }

    const results = [];
    const searchPath = search_dir ? path.join(DATA_DIRECTORY, path.normalize(search_dir)) : DATA_DIRECTORY;

    // Prevent path traversal
    if (!searchPath.startsWith(DATA_DIRECTORY)) {
        return res.status(400).json({ error: 'Invalid search directory' });
    }

    fs.readdir(searchPath, (err, files) => {
        if (err) {
            console.error(err);
            return res.status(400).json({ error: 'Error reading directory' });
        }

        files.forEach(file => {
            const filePath = path.join(searchPath, file);
            const isFile = fs.statSync(filePath).isFile();

            if (isFile) {
                let contentMatches = true;
                let nameMatches = true;

                if (search_content) {
                    const fileContent = fs.readFileSync(filePath, 'utf8');
                    contentMatches = fileContent.includes(search_content);
                }
                if (search_filename) {
                    nameMatches = file === search_filename;
                }

                if (contentMatches || nameMatches) {
                    results.push(filePath);
                }
            }
        });

        res.json({ files: results });
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});