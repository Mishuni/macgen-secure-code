const express = require('express');
const fs = require('fs');
const path = require('path');
const validator = require('validator'); // Importing validator for input validation
const app = express();
const PORT = 5000;
const logFilePath = path.join(__dirname, 'logs.txt');

// Middleware to sanitize input
function sanitizeInput(input) {
    return input.replace(/[\n\r]/g, ''); // Remove newline characters
}

app.use(express.json());

// Middleware to check for valid log messages
function validateLogMessage(req, res, next) {
    const { message } = req.body;
    if (typeof message !== 'string' || !validator.isLength(message, { min: 1 })) {
        return res.status(400).send('Invalid message format');
    }
    next();
}

app.post('/log', validateLogMessage, (req, res) => {
    const { message } = req.body;
    const sanitizedMessage = sanitizeInput(message);

    fs.appendFile(logFilePath, sanitizedMessage + '\n', { mode: 0o600 }, (err) => {
        if (err) {
            console.error('Error writing to log file', err);
            return res.status(500).send('Internal Server Error');
        }
        res.status(200).send('Log message successful');
    });
});

// Middleware to restrict access to logs
function restrictLogAccess(req, res, next) {
    // Placeholder for authentication logic
    // Implement authentication and authorization here
    next();
}

app.get('/logs', restrictLogAccess, (req, res) => {
    fs.readFile(logFilePath, 'utf8', (err, data) => {
        if (err) {
            console.error('Error reading log file', err);
            return res.status(500).send('Internal Server Error');
        }
        res.type('text/plain').send(data);
    });
});

// Log rotation logic (basic implementation)
const logFileSizeLimit = 10 * 1024 * 1024; // 10 MB
setInterval(() => {
    fs.stat(logFilePath, (err, stats) => {
        if (!err && stats.size > logFileSizeLimit) {
            fs.rename(logFilePath, logFilePath + '.old', (err) => {
                if (err) {
                    console.error('Error rotating log file', err);
                }
            });
        }
    });
}, 60000); // Check every minute

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});