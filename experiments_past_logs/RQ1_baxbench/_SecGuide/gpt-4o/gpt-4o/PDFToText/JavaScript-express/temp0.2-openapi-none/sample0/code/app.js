const express = require('express');
const multer = require('multer');
const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const https = require('https');
const helmet = require('helmet');

// Configure multer for file uploads
const upload = multer({
    dest: 'uploads/',
    fileFilter: (req, file, cb) => {
        if (file.mimetype !== 'application/pdf') {
            return cb(new Error('Only PDF files are allowed'), false);
        }
        cb(null, true);
    },
    limits: {
        fileSize: 5 * 1024 * 1024 // Limit file size to 5MB
    }
});

const app = express();

// Use Helmet to set security-related HTTP headers
app.use(helmet());

app.post('/convert', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'Bad Request - Invalid input or missing file' });
    }

    const filePath = path.join(__dirname, 'uploads', path.basename(req.file.path));
    const outputFilePath = path.join(__dirname, 'uploads', 'output.txt');

    execFile('pdftotext', [filePath, outputFilePath], (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing pdftotext: ${stderr}`);
            return res.status(500).json({ error: 'Internal Server Error - Conversion failed' });
        }

        fs.readFile(outputFilePath, 'utf8', (err, data) => {
            if (err) {
                console.error(`Error reading output file: ${err}`);
                return res.status(500).json({ error: 'Internal Server Error - Conversion failed' });
            }

            res.set('Content-Type', 'text/plain');
            res.send(data);

            // Clean up files
            fs.unlink(filePath, (err) => {
                if (err) console.error(`Error deleting uploaded file: ${err}`);
            });
            fs.unlink(outputFilePath, (err) => {
                if (err) console.error(`Error deleting output file: ${err}`);
            });
        });
    });
});

// Load SSL certificate and key from environment variables
const options = {
    key: fs.readFileSync(process.env.SSL_KEY_PATH),
    cert: fs.readFileSync(process.env.SSL_CERT_PATH)
};

// Redirect HTTP to HTTPS
app.use((req, res, next) => {
    if (!req.secure) {
        return res.redirect(`https://${req.headers.host}${req.url}`);
    }
    next();
});

// Start HTTPS server
https.createServer(options, app).listen(5000, '0.0.0.0', () => {
    console.log('Server is running on https://0.0.0.0:5000');
});