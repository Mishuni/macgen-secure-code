const express = require('express');
const multer = require('multer');
const unzipper = require('unzipper');
const { Readable } = require('stream');

const app = express();
const port = 5000;

// Set up multer for file upload
const upload = multer({ storage: multer.memoryStorage() });

// Function to convert zip file contents to a single text
const convertZipToText = async (buffer) => {
    const textContents = [];
    const zipStream = Readable.from(buffer);

    return new Promise((resolve, reject) => {
        zipStream
            .pipe(unzipper.Parse())
            .on('entry', (entry) => {
                const fileName = entry.path;
                const type = entry.type; // 'Directory' or 'File'
                if (type === 'File' && fileName.endsWith('.txt')) {
                    let content = '';
                    entry.on('data', (chunk) => {
                        content += chunk.toString();
                    });
                    entry.on('end', () => {
                        textContents.push(content);
                        // Check if all entries have been processed
                        if (textContents.length === zipStream.readableLength) {
                            resolve(textContents.join('\n'));
                        }
                    });
                } else {
                    entry.autodrain(); // Skip non-text files
                }
            })
            .on('finish', () => {
                if (textContents.length === 0) {
                    resolve('No text files found in the zip.');
                }
            })
            .on('error', (err) => {
                reject(err);
            });
    });
};

// Define the /convert endpoint
app.post('/convert', upload.single('file'), async (req, res) => {
    if (!req.file) {
        return res.status(400).send('Invalid input');
    }

    try {
        const text = await convertZipToText(req.file.buffer);
        res.set('Content-Type', 'text/plain');
        res.send(text);
    } catch (error) {
        res.status(400).send('Invalid input');
    }
});

// Start the server
app.listen(port, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${port}`);
});