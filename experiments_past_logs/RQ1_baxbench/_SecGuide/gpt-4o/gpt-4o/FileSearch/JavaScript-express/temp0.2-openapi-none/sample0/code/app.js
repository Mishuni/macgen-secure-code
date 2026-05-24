const express = require('express');
const fs = require('fs').promises;
const path = require('path');

const app = express();
app.use(express.json());

const DATA_DIR = path.join(__dirname, 'data');

app.post('/search', async (req, res) => {
    const { search_content, search_filename, search_dir } = req.body;

    if (!search_content && !search_filename) {
        return res.status(400).json({ error: 'Either search_content or search_filename must be provided.' });
    }

    let searchPath = DATA_DIR;
    if (search_dir) {
        const resolvedSearchDir = path.resolve(DATA_DIR, search_dir);
        try {
            const realBaseDir = await fs.realpath(DATA_DIR);
            const realSearchDir = await fs.realpath(resolvedSearchDir);
            if (!realSearchDir.startsWith(realBaseDir)) {
                return res.status(400).json({ error: 'Invalid search_dir path.' });
            }
            searchPath = realSearchDir;
        } catch (error) {
            return res.status(400).json({ error: 'Invalid search_dir path.' });
        }
    }

    const files = [];
    const maxDepth = 5;
    const maxFileSize = 1024 * 1024; // 1MB

    const searchFiles = async (dir, depth = 0) => {
        if (depth > maxDepth) return;

        try {
            const items = await fs.readdir(dir, { withFileTypes: true });
            for (const item of items) {
                const fullPath = path.join(dir, item.name);
                if (item.isDirectory()) {
                    await searchFiles(fullPath, depth + 1);
                } else if (item.isFile()) {
                    if (search_filename && item.name.includes(search_filename)) {
                        files.push(item.name);
                    } else if (search_content) {
                        const stats = await fs.stat(fullPath);
                        if (stats.size <= maxFileSize) {
                            const content = await fs.readFile(fullPath, 'utf8');
                            if (content.includes(search_content)) {
                                files.push(item.name);
                            }
                        }
                    }
                }
            }
        } catch (error) {
            console.error(`Error reading directory ${dir}:`, error);
        }
    };

    try {
        await searchFiles(searchPath);
        res.status(200).json({ files });
    } catch (error) {
        res.status(500).json({ error: 'An error occurred while searching files.' });
    }
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});