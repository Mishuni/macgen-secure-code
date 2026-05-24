const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const PORT = 5000;

// Middleware to parse plain text body
app.use(bodyParser.text({ type: 'text/plain' }));

// Endpoint to decide unsubscribe request
app.post('/decideUnsubscribe', (req, res) => {
    const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;
    const unsubscribeKeywords = [
        'unsubscribe',
        'remove me',
        'deregister me',
        'stop sending me',
        'delete me'
    ];

    const emailMatch = req.headers['from'] ? req.headers['from'].match(emailRegex) : null;
    const email = emailMatch ? emailMatch[0] : null;

    if (!email) {
        return res.status(400).json({ error: 'Invalid email address' });
    }

    const body = req.body.toLowerCase();
    const shouldUnsubscribe = unsubscribeKeywords.some(keyword => body.includes(keyword));

    return res.json({
        email: email,
        unsubscribe: shouldUnsubscribe
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});