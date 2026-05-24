
const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.text({ limit: '10kb' }));

const PORT = 5000;

app.post('/decideUnsubscribe', (req, res) => {
    const emailContent = req.body;
    const unsubscribeKeywords = [
        "unsubscribe", 
        "remove me", 
        "deregister me", 
        "stop sending me", 
        "delete me"
    ];

    const emailRegex = /From:\s*([^<]+)<([^>]+)>/i;
    const emailMatch = emailContent.match(emailRegex);
    if (!emailMatch) {
        return res.status(400).json({ error: "Invalid email format" });
    }

    const emailAddress = emailMatch[2].trim();
    if (!emailAddress) {
        return res.status(400).json({ error: "Email address not found" });
    }

    const lowerCaseContent = emailContent.toLowerCase();
    const unsubscribe = unsubscribeKeywords.some(keyword => lowerCaseContent.includes(keyword));

    res.status(200).json({
        email: emailAddress,
        unsubscribe: unsubscribe
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});