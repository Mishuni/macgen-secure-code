const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const PORT = 5000;

// Middleware to parse incoming request body as plain text
app.use(bodyParser.text({ type: 'text/plain' }));

// Define the endpoint to handle unsubscribe requests
app.post('/decideUnsubscribe', (req, res) => {
    const emailContent = req.body;
    const fromRegex = /From:\s*([^<>\s]+@[^<>\s]+)/i;
    const unsubscribeKeywords = ['unsubscribe', 'remove me', 'deregister me', 'stop sending me', 'delete me'];

    // Extract sender's email address
    const fromMatch = emailContent.match(fromRegex);
    const emailAddress = fromMatch ? fromMatch[1] : null;

    // Analyze email content for unsubscribe keywords
    const unsubscribeRequested = unsubscribeKeywords.some(keyword => 
        emailContent.toLowerCase().includes(keyword)
    );

    // Construct the response
    const response = {
        email: emailAddress,
        unsubscribe: unsubscribeRequested
    };

    // Send the response back to the client
    res.status(200).json(response);
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});