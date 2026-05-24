const express = require('express');
const cookieParser = require('cookie-parser');
const { v4: uuidv4 } = require('uuid');
const helmet = require('helmet');
const csurf = require('csurf');
const rateLimit = require('express-rate-limit');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
app.use(express.json());
app.use(cookieParser());
app.use(helmet());

const PORT = process.env.PORT || 5000;
const HOST = process.env.HOST || '0.0.0.0';

// Rate limiting middleware
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
    message: 'Too many requests, please try again later.'
});
app.use(limiter);

// CSRF protection middleware
const csrfProtection = csurf({
    cookie: {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'Strict'
    }
});
app.use(csrfProtection);

// Helper function to extract email from raw email text
function extractEmail(rawEmail) {
    const emailMatch = rawEmail.match(/From:.*<(.+?)>/);
    return emailMatch ? emailMatch[1] : null;
}

// Helper function to decide if the email contains unsubscribe keywords
function shouldUnsubscribe(rawEmail) {
    const unsubscribeKeywords = [
        "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
    ];
    const lowerCaseEmail = rawEmail.toLowerCase();
    return unsubscribeKeywords.some(keyword => lowerCaseEmail.includes(keyword));
}

// Middleware for input validation
function validateRequestBody(req, res, next) {
    if (typeof req.body !== 'object' || !req.body.rawEmail || !req.body.csrfToken) {
        return res.status(400).json({ error: 'Invalid request format' });
    }
    const email = extractEmail(req.body.rawEmail);
    if (!email) {
        return res.status(400).json({ error: 'Invalid email format' });
    }
    next();
}

// Centralized error handling middleware
app.use((err, req, res, next) => {
    if (err.code === 'EBADCSRFTOKEN') {
        return res.status(403).json({ error: 'Invalid CSRF token' });
    }
    console.error(err.stack);
    res.status(500).json({ error: 'Internal Server Error' });
});

app.post('/decideUnsubscribe', validateRequestBody, (req, res) => {
    const rawEmail = req.body.rawEmail;
    const email = extractEmail(rawEmail);
    const unsubscribe = shouldUnsubscribe(rawEmail);

    res.json({ email, unsubscribe });
});

app.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}/`);
});