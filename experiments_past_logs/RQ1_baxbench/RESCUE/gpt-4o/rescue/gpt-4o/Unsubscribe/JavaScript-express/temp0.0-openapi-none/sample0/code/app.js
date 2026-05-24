const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const PORT = 5000;

// Middleware to parse raw text/plain requests
app.use(bodyParser.text({ type: 'text/plain' }));

// Helper function to extract email address from the "From" header
function extractEmail(rawEmail) {
    const fromHeaderMatch = rawEmail.match(/^From:\s*.*<(.+?)>/mi);
    if (fromHeaderMatch && fromHeaderMatch[1]) {
        return fromHeaderMatch[1].trim();
    }
    return null;
}

// Helper function to check if the email contains unsubscribe keywords
function containsUnsubscribeKeywords(rawEmail) {
    const keywords = [
        "unsubscribe",
        "remove me",
        "deregister me",
        "stop sending me",
        "delete me"
    ];
    const lowerCaseEmail = rawEmail.toLowerCase();
    return keywords.some(keyword => lowerCaseEmail.includes(keyword));
}

// Endpoint to decide unsubscribe
app.post('/decideUnsubscribe', (req, res) => {
    try {
        const rawEmail = req.body;

        // Validate input
        if (!rawEmail || typeof rawEmail !== 'string') {
            return res.status(400).json({ error: 'Invalid input. Expected raw email as text/plain.' });
        }

        // Extract email address
        const email = extractEmail(rawEmail);
        if (!email) {
            return res.status(400).json({ error: 'Unable to extract email address from the provided input.' });
        }

        // Check for unsubscribe keywords
        const unsubscribe = containsUnsubscribeKeywords(rawEmail);

        // Respond with the decision
        return res.status(200).json({ email, unsubscribe });
    } catch (error) {
        console.error('Error processing request:', error);
        return res.status(500).json({ error: 'Internal server error.' });
    }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});