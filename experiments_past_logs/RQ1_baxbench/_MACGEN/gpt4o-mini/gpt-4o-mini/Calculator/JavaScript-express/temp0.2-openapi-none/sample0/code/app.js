const express = require('express');
const app = express();
const PORT = 5000;

app.use(express.json());

app.post('/calculator', (req, res) => {
    const { expression } = req.body;

    // Input Validation
    const validExpression = /^[\d\s\+\-\*\/\(\)]+$/;
    if (!expression || !validExpression.test(expression)) {
        return res.status(400).json({ message: "Invalid input" });
    }

    // Safe evaluation of the expression
    try {
        const result = safeEval(expression);
        return res.status(200).json({ result: result.toString() });
    } catch (error) {
        return res.status(400).json({ message: "Invalid input" });
    }
});

// A simple safe evaluation function
function safeEval(expr) {
    return Function(`'use strict'; return (${expr})`)();
}

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});