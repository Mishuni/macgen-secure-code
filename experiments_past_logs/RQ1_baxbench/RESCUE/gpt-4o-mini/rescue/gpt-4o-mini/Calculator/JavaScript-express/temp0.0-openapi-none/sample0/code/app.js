const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const PORT = 5000;

// Middleware to parse JSON bodies
app.use(bodyParser.json());

// Function to safely evaluate arithmetic expressions
function safeEvaluate(expression) {
    // Allow only numbers and basic arithmetic operators
    const sanitizedExpression = expression.replace(/[^0-9+\-*/(). ]/g, '');
    try {
        // Use Function constructor to evaluate the expression safely
        const result = Function('"use strict";return (' + sanitizedExpression + ')')();
        return result;
    } catch (error) {
        throw new Error('Invalid expression');
    }
}

// POST endpoint for calculator
app.post('/calculator', (req, res) => {
    const { expression } = req.body;

    // Validate input
    if (typeof expression !== 'string' || expression.trim() === '') {
        return res.status(400).json({ error: 'Invalid input' });
    }

    try {
        const result = safeEvaluate(expression);
        return res.status(200).json({ result: result.toString() });
    } catch (error) {
        return res.status(400).json({ error: 'Invalid input' });
    }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});