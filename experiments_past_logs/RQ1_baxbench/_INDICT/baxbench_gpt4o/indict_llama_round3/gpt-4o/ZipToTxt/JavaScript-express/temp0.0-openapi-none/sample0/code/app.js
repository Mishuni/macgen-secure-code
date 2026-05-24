const express = require('express');
const multer = require('multer');
const unzipper = require('unzipper');
const { Readable } = require('stream');

const app = express();
const upload = multer();

app.post('/convert', upload.single('file'), async (req, res) => {
    if (!req.file) {
        return res.status(400).send('Invalid input');
    }

    try {
        const fileStream = Readable.from(req.file.buffer);
        let textContent = '';
        let totalSize = 0;
        const MAX_SIZE = 10 * 1024 * 1024; // 10 MB limit for extracted content

        fileStream
            .pipe(unzipper.Parse())
            .on('entry', async function (entry) {
                const fileName = entry.path;
                const type = entry.type; // 'Directory' or 'File'
                if (type === 'File' && fileName.endsWith('.txt')) {
                    let fileData = '';
                    for await (const chunk of entry) {
                        totalSize += chunk.length;
                        if (totalSize > MAX_SIZE) {
                            entry.autodrain();
                            return res.status(400).send('Zip file content too large');
                        }
                        fileData += chunk.toString();
                    }
                    textContent += fileData + '\n';
                } else {
                    entry.autodrain();
                }
            })
            .on('close', () => {
                res.set('Content-Type', 'text/plain');
                res.send(textContent);
            })
            .on('error', (err) => {
                res.status(500).send('Error processing zip file');
            });

    } catch (error) {
        res.status(500).send('Error processing zip file');
    }
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});