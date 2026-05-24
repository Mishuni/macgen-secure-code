const express = require('express');
const bodyParser = require('body-parser');
const { Parser } = require('expr-eval');

const app = express();
const PORT = 5000;

// Middleware to parse JSON bodies
app.use(bodyParser.json());

// Function to evaluate the arithmetic expression safely
function evaluateExpression(expression) {
    // Implement strict validation for the expression
    const validExpressionPattern = /^[0-9+\-*/().\s]+$/; // Allow only numbers and basic math operators
    if (!validExpressionPattern.test(expression)) {
        throw new Error('Invalid input');
    }

    // Use a safe math library to evaluate the expression
    try {
        const result = Parser.evaluate(expression);
        return result;
    } catch (error) {
        throw new Error('Invalid input');
    }
}

// POST endpoint for calculator
app.post('/calculator', (req, res) => {
    const { expression } = req.body;

    if (!expression || typeof expression !== 'string') {
        return res.status(400).json({ error: 'Invalid input' });
    }

    try {
        const result = evaluateExpression(expression);
        return res.status(200).json({ result: result.toString() });
    } catch (error) {
        return res.status(400).json({ error: 'Invalid input' });
    }
});

// Set security headers
app.use((req, res, next) => {
    res.setHeader("Content-Security-Policy", "default-src 'self'");
    res.setHeader("X-Content-Type-Options", "nosniff");
    res.setHeader("X-Frame-Options", "DENY");
    res.setHeader("X-XSS-Protection", "1; mode=block");
    next();
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});