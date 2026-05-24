const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

function evaluateExpression(expression) {
    // Only allow numbers, operators, and spaces
    if (!/^[0-9+\-*/().\s]+$/.test(expression)) {
        throw new Error('Invalid characters in expression');
    }

    // Implement a simple parser to evaluate the expression safely
    try {
        // Tokenize the expression
        const tokens = expression.match(/[+\-*/()]|\d+(\.\d+)?/g);
        if (!tokens) throw new Error('Invalid expression');

        // Shunting Yard Algorithm to convert infix to postfix
        const outputQueue = [];
        const operatorStack = [];
        const precedence = { '+': 1, '-': 1, '*': 2, '/': 2 };
        const associativity = { '+': 'L', '-': 'L', '*': 'L', '/': 'L' };

        tokens.forEach(token => {
            if (!isNaN(token)) {
                outputQueue.push(parseFloat(token));
            } else if ('+-*/'.includes(token)) {
                while (
                    operatorStack.length &&
                    '*/+-'.includes(operatorStack[operatorStack.length - 1]) &&
                    ((associativity[token] === 'L' && precedence[token] <= precedence[operatorStack[operatorStack.length - 1]]) ||
                    (associativity[token] === 'R' && precedence[token] < precedence[operatorStack[operatorStack.length - 1]]))
                ) {
                    outputQueue.push(operatorStack.pop());
                }
                operatorStack.push(token);
            } else if (token === '(') {
                operatorStack.push(token);
            } else if (token === ')') {
                while (operatorStack.length && operatorStack[operatorStack.length - 1] !== '(') {
                    outputQueue.push(operatorStack.pop());
                }
                operatorStack.pop();
            }
        });

        while (operatorStack.length) {
            outputQueue.push(operatorStack.pop());
        }

        // Evaluate the postfix expression
        const stack = [];
        outputQueue.forEach(token => {
            if (!isNaN(token)) {
                stack.push(token);
            } else {
                const b = stack.pop();
                const a = stack.pop();
                switch (token) {
                    case '+': stack.push(a + b); break;
                    case '-': stack.push(a - b); break;
                    case '*': stack.push(a * b); break;
                    case '/': 
                        if (b === 0) throw new Error('Division by zero');
                        stack.push(a / b); 
                        break;
                }
            }
        });

        return stack[0];
    } catch (error) {
        throw new Error('Invalid expression');
    }
}

app.post('/calculator', (req, res) => {
    const { expression } = req.body;

    if (typeof expression !== 'string') {
        return res.status(400).json({ error: 'Invalid input: Expression must be a string' });
    }

    try {
        const result = evaluateExpression(expression);
        res.status(200).json({ result: result.toString() });
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});