const express = require('express');
const bodyParser = require('body-parser');
const math = require('mathjs');

const app = express();
const PORT = 5000;

// Middleware to parse JSON bodies
app.use(bodyParser.json());

// Define the /calculator endpoint
app.post('/calculator', (req, res) => {
    // Validate content-type
    if (req.headers['content-type'] !== 'application/json') {
        return res.status(400).json({ error: 'Invalid content-type' });
    }

    const { expression } = req.body;

    // Validate the request body
    if (typeof expression !== 'string') {
        return res.status(400).json({ error: 'Invalid input: expression must be a string' });
    }

    // Validate the expression to ensure it contains only safe characters
    const safePattern = /^[\d\s+\-*/()]+$/;
    if (!safePattern.test(expression)) {
        return res.status(400).json({ error: 'Invalid input: expression contains unsafe characters' });
    }

    try {
        // Evaluate the arithmetic expression safely
        const result = math.evaluate(expression);
        res.status(200).json({ result: result.toString() });
    } catch (error) {
        // Handle any errors that occur during evaluation
        res.status(400).json({ error: 'Invalid input: unable to evaluate expression' });
    }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});