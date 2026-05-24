const express = require('express');
const multer = require('multer');
const unzipper = require('unzipper');
const { Readable } = require('stream');
const fileType = require('file-type');
const path = require('path');
const helmet = require('helmet');
const cors = require('cors');
const morgan = require('morgan');

const app = express();
const port = 5000;

// Middleware for security headers
app.use(helmet());

// CORS configuration
app.use(cors({
    origin: 'http://your-allowed-origin.com', // Replace with your allowed origin
    methods: ['POST'],
}));

// Logging middleware
app.use(morgan('combined'));

// Set up multer for file upload with strict MIME type validation
const upload = multer({
    limits: { fileSize: 10 * 1024 * 1024 }, // Limit to 10MB
    fileFilter: async (req, file, cb) => {
        const buffer = file.buffer;
        const type = await fileType.fromBuffer(buffer);
        if (type && type.mime === 'application/zip') {
            cb(null, true);
        } else {
            cb(new Error('Invalid file type. Only .zip files are allowed.'));
        }
    }
});

app.post('/convert', upload.single('file'), async (req, res) => {
    if (!req.file) {
        return res.status(400).send('Invalid input: No file uploaded.');
    }

    try {
        const textContents = [];
        const zipStream = Readable.from(req.file.buffer);

        // Unzip the contents
        zipStream
            .pipe(unzipper.Parse())
            .on('entry', (entry) => {
                const fileName = path.basename(entry.path); // Sanitize file name

                // Only process text files
                if (fileName.endsWith('.txt')) {
                    let content = '';
                    entry.on('data', (chunk) => {
                        content += chunk.toString();
                    });
                    entry.on('end', () => {
                        textContents.push(content);
                    });
                } else {
                    entry.autodrain(); // Skip non-text files
                }
            })
            .on('finish', () => {
                // Concatenate all text contents
                const finalText = textContents.join('\n');
                res.set('Content-Type', 'text/plain');
                res.send(finalText);
            })
            .on('error', (err) => {
                console.error(err);
                res.status(400).send('Error processing zip file.');
            });
    } catch (error) {
        console.error(error);
        res.status(400).send('Error processing request.');
    }
});

app.listen(port, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${port}`);
});