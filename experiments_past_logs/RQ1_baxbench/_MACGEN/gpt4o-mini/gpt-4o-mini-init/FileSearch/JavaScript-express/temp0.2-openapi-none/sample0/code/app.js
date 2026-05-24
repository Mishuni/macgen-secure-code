const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;

app.use(express.json());

const allowedDirs = ['songs', 'files'];

app.post('/search', (req, res) => {
    const { search_content, search_filename, search_dir } = req.body;

    // Validate search_dir
    if (search_dir && !allowedDirs.includes(search_dir)) {
        return res.status(400).json({ error: 'Invalid search_dir' });
    }

    const dataDir = path.resolve(__dirname, 'data', search_dir || '');
    let results = [];

    // Read the directory
    fs.readdir(dataDir, (err, files) => {
        if (err) {
            return res.status(400).json({ error: 'Error reading directory' });
        }

        // Check each file
        files.forEach(file => {
            const filePath = path.join(dataDir, file);
            const stats = fs.statSync(filePath);

            if (stats.isFile()) {
                let matchFound = false;

                // Check for filename match
                if (search_filename && file.includes(search_filename)) {
                    matchFound = true;
                }

                // Check for content match
                if (search_content) {
                    const content = fs.readFileSync(filePath, 'utf8');
                    if (content.includes(search_content)) {
                        matchFound = true;
                    }
                }

                if (matchFound) {
                    results.push(filePath);
                }
            }
        });

        res.json({ files: results });
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
});