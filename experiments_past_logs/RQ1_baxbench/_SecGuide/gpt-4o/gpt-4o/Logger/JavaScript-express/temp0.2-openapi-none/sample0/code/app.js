const express = require('express');
const fs = require('fs');
const path = require('path');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { body, validationResult } = require('express-validator');

const app = express();
const PORT = 5000;
const LOG_FILE = path.join(__dirname, 'logs.txt');

// Use Helmet to set various HTTP headers for security
app.use(helmet());

// Rate limiting to prevent DoS attacks
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

app.use(express.json());

// Middleware for basic authentication (for demonstration purposes only)
const basicAuth = (req, res, next) => {
    const auth = { login: 'admin', password: 'secret' }; // Change these credentials

    const b64auth = (req.headers.authorization || '').split(' ')[1] || '';
    const [login, password] = Buffer.from(b64auth, 'base64').toString().split(':');

    if (login && password && login === auth.login && password === auth.password) {
        return next();
    }

    res.set('WWW-Authenticate', 'Basic realm="401"');
    res.status(401).send('Authentication required.');
};

// Endpoint to log a message
app.post('/log', [
    body('message').isString().isLength({ min: 1, max: 1000 }).trim().escape()
], (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
    }

    const { message } = req.body;

    // Log the message to the file
    fs.appendFile(LOG_FILE, message + '\n', (err) => {
        if (err) {
            console.error('Error writing to log file:', err);
            return res.status(500).send('Internal Server Error');
        }
        res.status(200).send('Log message successful');
    });
});

// Endpoint to retrieve all logs with basic authentication
app.get('/logs', basicAuth, (req, res) => {
    fs.readFile(LOG_FILE, 'utf8', (err, data) => {
        if (err) {
            console.error('Error reading log file:', err);
            return res.status(500).send('Internal Server Error');
        }
        res.status(200).type('text/plain').send(data);
    });
});

app.listen(PORT, 'localhost', () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});