const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const PORT = 5000;

// Middleware to parse JSON request bodies
app.use(bodyParser.json());

// Helper function to safely evaluate arithmetic expressions
function evaluateExpression(expression) {
    // Only allow numbers, operators (+, -, *, /), and parentheses
    const validCharacters = /^[0-9+\-*/().\s]+$/;
    if (!validCharacters.test(expression)) {
        throw new Error('Invalid characters in expression');
    }

    // Use Function constructor to safely evaluate the expression
    // This ensures that only valid arithmetic expressions are evaluated
    try {
        // eslint-disable-next-line no-new-func
        const result = new Function(`return (${expression})`)();
        if (typeof result !== 'number' || !isFinite(result)) {
            throw new Error('Invalid arithmetic operation');
        }
        return result;
    } catch (error) {
        throw new Error('Error evaluating expression');
    }
}

// POST /calculator endpoint
app.post('/calculator', (req, res) => {
    const { expression } = req.body;

    // Validate input
    if (!expression || typeof expression !== 'string') {
        return res.status(400).json({ error: 'Invalid input: expression is required and must be a string' });
    }

    try {
        // Evaluate the arithmetic expression
        const result = evaluateExpression(expression);

        // Respond with the result
        return res.status(200).json({ result: result.toString() });
    } catch (error) {
        // Handle errors (e.g., invalid characters or invalid arithmetic operations)
        return res.status(400).json({ error: error.message });
    }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});