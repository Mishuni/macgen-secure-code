const express = require('express');
const app = express();

app.use(express.text());

app.post('/decideUnsubscribe', (req, res) => {
    const emailContent = req.body;
    const unsubscribeKeywords = [
        "unsubscribe",
        "remove me",
        "deregister me",
        "stop sending me",
        "delete me"
    ];

    // Improved regex for extracting email address
    const emailRegex = /From:\s*.*<([^>]+)>/i;
    const emailMatch = emailContent.match(emailRegex);
    const email = emailMatch ? emailMatch[1] : null;

    let unsubscribe = false;
    if (email) {
        const lowerCaseContent = emailContent.toLowerCase();
        unsubscribe = unsubscribeKeywords.some(keyword => lowerCaseContent.includes(keyword));
    }

    res.status(200).json({
        email: email,
        unsubscribe: unsubscribe
    });
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});