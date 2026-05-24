const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const PORT = 5000;

// Middleware to parse JSON request bodies
app.use(bodyParser.json());

// POST endpoint to calculate the result of an arithmetic expression
app.post('/calculator', (req, res) => {
    // Validate Content-Type
    if (req.headers['content-type'] !== 'application/json') {
        return res.status(400).json({ error: 'Invalid Content-Type' });
    }

    const { expression } = req.body;

    // Validate input
    if (typeof expression !== 'string' || !/^[\d\s()+\-*/.]+$/.test(expression)) {
        return res.status(400).json({ error: 'Invalid input: expression contains unsafe characters' });
    }

    try {
        // Use a safe evaluation method
        const result = safeEval(expression);
        return res.status(200).json({ result: result.toString() });
    } catch (error) {
        return res.status(400).json({ error: 'Invalid input: unable to evaluate expression' });
    }
});

// Safe evaluation function
function safeEval(expr) {
    // Create a new function to evaluate the expression safely
    return Function('"use strict";return (' + expr + ')')();
}

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});