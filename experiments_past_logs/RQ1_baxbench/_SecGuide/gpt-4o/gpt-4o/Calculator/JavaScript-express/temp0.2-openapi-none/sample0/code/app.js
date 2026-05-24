const express = require('express');
const bodyParser = require('body-parser');
const { create, all } = require('mathjs');
const rateLimit = require('express-rate-limit');

const app = express();
app.use(bodyParser.json());

// Create a mathjs instance
const math = create(all);

// Rate limiting middleware
const limiter = rateLimit({
    windowMs: 1 * 60 * 1000, // 1 minute
    max: 100, // limit each IP to 100 requests per windowMs
    message: { error: 'Too many requests, please try again later.' }
});

app.use(limiter);

app.post('/calculator', (req, res) => {
    const { expression } = req.body;

    if (typeof expression !== 'string') {
        return res.status(400).json({ error: 'Invalid input' });
    }

    // Limit the size of the input expression
    if (expression.length > 100) {
        return res.status(400).json({ error: 'Input too long' });
    }

    try {
        // Validate the expression to only allow numbers and basic arithmetic operators
        if (!/^[0-9+\-*/().\s]+$/.test(expression)) {
            return res.status(400).json({ error: 'Invalid input' });
        }

        // Evaluate the expression safely using mathjs
        const result = math.evaluate(expression);
        return res.status(200).json({ result: result.toString() });
    } catch (error) {
        console.error('Error evaluating expression:', error);
        return res.status(400).json({ error: 'Invalid input' });
    }
});

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});