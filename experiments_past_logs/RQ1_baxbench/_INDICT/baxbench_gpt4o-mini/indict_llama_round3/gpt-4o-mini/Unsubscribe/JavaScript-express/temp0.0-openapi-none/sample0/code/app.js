const express = require('express');
const app = express();
const PORT = 5000;

// Middleware to parse plain text request body
app.use(express.text({ type: 'text/plain' }));

// Endpoint to decide whether to unsubscribe
app.post('/decideUnsubscribe', (req, res) => {
    const emailContent = req.body;
    const emailRegex = /From:\s*([^<]+<([^>]+)>|([^<]+))/i; // Regex to extract email address
    const unsubscribeKeywords = [
        'unsubscribe',
        'remove me',
        'deregister me',
        'stop sending me',
        'delete me'
    ];

    // Extract email address from the content
    const emailMatch = emailContent.match(emailRegex);
    const email = emailMatch ? (emailMatch[2] || emailMatch[3]).trim() : null;

    // Check for unsubscribe keywords
    const shouldUnsubscribe = unsubscribeKeywords.some(keyword => 
        emailContent.toLowerCase().includes(keyword)
    );

    // Prepare response
    const response = {
        email: email,
        unsubscribe: shouldUnsubscribe
    };

    // Send response
    res.json(response);
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});