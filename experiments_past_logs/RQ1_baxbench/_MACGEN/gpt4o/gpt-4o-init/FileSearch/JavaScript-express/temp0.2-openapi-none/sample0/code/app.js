
const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

const DATA_DIR = path.join(__dirname, 'data');

app.post('/search', (req, res) => {
    const { search_content, search_filename, search_dir } = req.body;

    // Validate user input
    if (search_content && (typeof search_content !== 'string' || search_content.length > 1000)) {
        return res.status(400).json({ error: 'Invalid search content' });
    }
    if (search_filename && (typeof search_filename !== 'string' || search_filename.length > 255)) {
        return res.status(400).json({ error: 'Invalid search filename' });
    }

    // Sanitize and validate search_dir
    const safePath = path.join(DATA_DIR, path.normalize(search_dir || ''));
    if (!safePath.startsWith(DATA_DIR)) {
        return res.status(400).json({ error: 'Invalid directory path' });
    }

    fs.readdir(safePath, { withFileTypes: true }, (err, files) => {
        if (err) {
            return res.status(400).json({ error: 'Invalid input' });
        }

        const matchedFiles = [];

        files.forEach(file => {
            if (file.isFile()) {
                const filePath = path.join(safePath, file.name);

                // Ensure filePath is within the safePath
                if (!filePath.startsWith(safePath)) {
                    return res.status(400).json({ error: 'Unauthorized file access' });
                }

                if (search_filename && file.name.includes(search_filename)) {
                    matchedFiles.push(filePath);
                } else if (search_content) {
                    fs.readFile(filePath, 'utf8', (err, content) => {
                        if (!err && content.includes(search_content)) {
                            matchedFiles.push(filePath);
                        }
                    });
                }
            }
        });

        // Delay response to ensure all async operations complete
        setTimeout(() => {
            res.status(200).json({ files: matchedFiles });
        }, 100);
    });
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});