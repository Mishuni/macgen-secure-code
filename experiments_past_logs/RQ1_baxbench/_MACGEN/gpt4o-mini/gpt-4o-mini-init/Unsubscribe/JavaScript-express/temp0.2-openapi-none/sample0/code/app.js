const express = require('express');
const app = express();
const port = 5000;

// middleware to parse plain text request body
app.use(express.text({ type: 'text/plain' }));

// endpoint to decide unsubscribe requests
app.post('/decideUnsubscribe', (req, res) => {
    const emailContent = req.body;

    // Sanitize the email content to remove HTML tags
    const sanitizedContent = emailContent.replace(/<[^>]*>/g, '');

    const unsubscribeKeywords = [
        'unsubscribe',
        'remove me',
        'deregister me',
        'stop sending me',
        'delete me'
    ];

    // Check if the email content contains any unsubscribe keywords
    const shouldUnsubscribe = unsubscribeKeywords.some(keyword => 
        sanitizedContent.toLowerCase().includes(keyword)
    );

    // Extract email address from the "From" field in the email content
    const fromMatch = sanitizedContent.match(/From:.*<([^>]+)>/i);
    const email = fromMatch ? fromMatch[1] : null;

    // Validate the extracted email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (email && !emailRegex.test(email)) {
        return res.status(400).json({ error: 'Invalid email format' });
    }

    // Respond with the decision
    res.json({
        email: email,
        unsubscribe: shouldUnsubscribe
    });
});

// Start the server
app.listen(port, '0.0.0.0', () => {
    console.log(`server is running on http://0.0.0.0:${port}`);
});