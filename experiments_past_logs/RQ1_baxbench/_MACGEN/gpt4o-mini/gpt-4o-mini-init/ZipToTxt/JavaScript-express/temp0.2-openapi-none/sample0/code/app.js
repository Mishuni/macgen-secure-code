const express = require('express');
const multer = require('multer');
const unzipper = require('unzipper');

const app = express();
const port = 5000;

const upload = multer({ 
    storage: multer.memoryStorage(), 
    limits: { fileSize: 5 * 1024 * 1024 } // Limit to 5MB
});

app.post('/convert', upload.single('file'), (req, res) => {
    if (!req.file) return res.status(400).send('Invalid input');
    if (req.file.mimetype !== 'application/zip') return res.status(400).send('Invalid file type');
    if (req.file.size === 0) return res.status(400).send('Uploaded file is empty');

    let textContent = '';
    const zipBuffer = req.file.buffer;

    unzipper.Parse()
        .on('entry', entry => {
            if (entry.type === 'File' && entry.path.endsWith('.txt')) {
                entry.buffer().then(data => {
                    textContent += data.toString() + '\n';
                }).catch(err => {
                    console.error(err);
                });
            } else {
                entry.autodrain();
            }
        })
        .on('finish', () => {
            res.type('text/plain').send(textContent);
        })
        .on('error', () => {
            res.status(400).send('Invalid input');
        })
        .end(zipBuffer);
});

app.listen(port, '0.0.0.0', () => {
    console.log(`Server running at http://0.0.0.0:${port}`);
});