const express = require('express');

const app = express();
const PORT = 5000;

app.use(express.json());

app.post('/calculator', (req, res) => {
    const { expression } = req.body;

    if (typeof expression !== 'string') {
        return res.status(400).json({ error: 'Invalid input' });
    }

    try {
        const result = evaluateExpression(expression);
        return res.status(200).json({ result: result.toString() });
    } catch (error) {
        return res.status(400).json({ error: 'Invalid input' });
    }
});

// A simple and safe expression evaluator
function evaluateExpression(expr) {
    // Allow only numbers, operators, and whitespace
    if (/^[0-9+\-*/().\s]+$/.test(expr)) {
        // Use a safer method to evaluate the expression
        return safeEval(expr);
    } else {
        throw new Error('Invalid expression');
    }
}

// A simple safe evaluation function
function safeEval(expr) {
    const tokens = expr.match(/(\d+|[-+*/()])/g);
    const output = [];
    const operators = [];
    
    const precedence = {
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2
    };

    const applyOperator = (b, a, op) => {
        switch (op) {
            case '+': return a + b;
            case '-': return a - b;
            case '*': return a * b;
            case '/': 
                if (b === 0) throw new Error('Division by zero');
                return a / b;
        }
    };

    for (const token of tokens) {
        if (!isNaN(token)) {
            output.push(Number(token));
        } else if (token in precedence) {
            while (operators.length && precedence[operators[operators.length - 1]] >= precedence[token]) {
                const op = operators.pop();
                const b = output.pop();
                const a = output.pop();
                output.push(applyOperator(b, a, op));
            }
            operators.push(token);
        } else if (token === '(') {
            operators.push(token);
        } else if (token === ')') {
            while (operators.length && operators[operators.length - 1] !== '(') {
                const op = operators.pop();
                const b = output.pop();
                const a = output.pop();
                output.push(applyOperator(b, a, op));
            }
            operators.pop(); // Remove the '('
        }
    }

    while (operators.length) {
        const op = operators.pop();
        const b = output.pop();
        const a = output.pop();
        output.push(applyOperator(b, a, op));
    }

    return output[0];
}

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});