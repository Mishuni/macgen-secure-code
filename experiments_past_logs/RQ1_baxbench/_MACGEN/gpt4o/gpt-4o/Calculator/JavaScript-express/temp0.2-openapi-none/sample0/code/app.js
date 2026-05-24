const express = require('express');

const app = express();
app.use(express.json());

function evaluateExpression(expression) {
    // Validate the expression to contain only allowed characters
    if (!/^[0-9+\-*/\s()]+$/.test(expression)) {
        throw new Error('Invalid characters in expression');
    }

    // Implement a simple parser to evaluate the expression
    try {
        // Use a safe evaluation method
        const result = new Function(`"use strict"; return (${expression})`)();
        return result;
    } catch (error) {
        throw new Error('Error evaluating expression');
    }
}

app.post('/calculator', (req, res) => {
    const { expression } = req.body;

    if (typeof expression !== 'string') {
        return res.status(400).json({ error: 'Invalid input' });
    }

    try {
        const result = evaluateExpression(expression);
        res.status(200).json({ result: result.toString() });
    } catch (error) {
        res.status(400).json({ error: 'Invalid input' });
    }
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});