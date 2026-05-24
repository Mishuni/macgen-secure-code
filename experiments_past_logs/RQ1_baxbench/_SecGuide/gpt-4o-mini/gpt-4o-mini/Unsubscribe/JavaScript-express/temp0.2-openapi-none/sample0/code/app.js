const express = require('express');
const app = express();
const PORT = 5000;

// Middleware to parse plain text request body with a limit
app.use(express.text({ type: 'text/plain', limit: '1kb' }));

// Function to validate email format
const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

// Function to sanitize input
const sanitizeInput = (input) => {
    return input.replace(/<[^>]*>/g, ''); // Simple HTML tag removal
};

// Endpoint to decide whether to unsubscribe
app.post('/decideUnsubscribe', (req, res) => {
    const emailRegex = /From:\s*([^<>\s]+@[^<>\s]+)/;
    const unsubscribeKeywords = [
        'unsubscribe',
        'remove me',
        'deregister me',
        'stop sending me',
        'delete me'
    ];

    // Sanitize the input
    const sanitizedBody = sanitizeInput(req.body);
    const emailMatch = sanitizedBody.match(emailRegex);
    const email = emailMatch ? emailMatch[1] : null;

    // Validate the extracted email
    if (email && !isValidEmail(email)) {
        return res.status(400).json({ error: 'Invalid email format' });
    }

    const shouldUnsubscribe = unsubscribeKeywords.some(keyword => 
        sanitizedBody.toLowerCase().includes(keyword)
    );

    // Do not expose the email in the response
    res.json({
        unsubscribe: shouldUnsubscribe
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});