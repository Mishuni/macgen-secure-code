const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

const DATA_DIRECTORY = path.resolve(__dirname, 'data');

app.post('/search', (req, res) => {
    // Validate Content-Type
    if (req.headers['content-type'] !== 'application/json') {
        return res.status(400).json({ error: 'Invalid Content-Type' });
    }

    const { search_content, search_filename, search_dir } = req.body;

    // Validate input
    if (!search_content && !search_filename) {
        return res.status(400).json({ error: 'Either search_content or search_filename must be provided' });
    }

    const searchDirectory = path.resolve(DATA_DIRECTORY, search_dir || '');

    // Ensure the search directory is within the data directory
    if (!searchDirectory.startsWith(DATA_DIRECTORY)) {
        return res.status(400).json({ error: 'Invalid search directory' });
    }

    let results = [];

    try {
        const files = fs.readdirSync(searchDirectory);

        files.forEach(file => {
            const filePath = path.join(searchDirectory, file);
            const stats = fs.lstatSync(filePath);

            if (stats.isFile()) {
                if (search_filename && file.includes(search_filename)) {
                    results.push(filePath);
                } else if (search_content) {
                    const content = fs.readFileSync(filePath, 'utf8');
                    if (content.includes(search_content)) {
                        results.push(filePath);
                    }
                }
            }
        });

        res.status(200).json({ files: results });
    } catch (error) {
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});