const express = require('express');
const app = express();
const PORT = 5000;

// Middleware to parse plain text
app.use(express.text());

// Helper function to extract email from raw email data
function extractEmail(rawEmail) {
    const emailRegex = /From:\s*.*<(.+?)>/i;
    const match = rawEmail.match(emailRegex);
    return match ? match[1] : null;
}

// Helper function to check for unsubscribe keywords
function containsUnsubscribeKeywords(emailContent) {
    const unsubscribeKeywords = [
        "unsubscribe",
        "remove me",
        "deregister me",
        "stop sending me",
        "delete me"
    ];
    const lowerCaseContent = emailContent.toLowerCase();
    return unsubscribeKeywords.some(keyword => lowerCaseContent.includes(keyword));
}

// POST endpoint to decide unsubscribe
app.post('/decideUnsubscribe', (req, res) => {
    const rawEmail = req.body;

    // Validate input
    if (!rawEmail || typeof rawEmail !== 'string') {
        return res.status(400).json({ error: 'Invalid email data' });
    }

    // Extract email address
    const email = extractEmail(rawEmail);
    if (!email) {
        return res.status(400).json({ error: 'Invalid email format' });
    }

    // Analyze email content
    const unsubscribe = containsUnsubscribeKeywords(rawEmail);

    // Construct response
    res.json({
        email: email,
        unsubscribe: unsubscribe
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});