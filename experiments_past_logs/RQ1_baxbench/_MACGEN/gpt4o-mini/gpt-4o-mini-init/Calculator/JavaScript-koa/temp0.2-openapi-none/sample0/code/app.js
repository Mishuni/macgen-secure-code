const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');

const app = new Koa();
const router = new Router();

router.post('/calculator', async (ctx) => {
    const { expression } = ctx.request.body;

    if (typeof expression !== 'string' || !isValidExpression(expression)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    try {
        const result = evaluateExpression(expression);
        ctx.body = { result: result.toString() };
    } catch (error) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
    }
});

function isValidExpression(expr) {
    // Basic validation to allow only numbers, operators, and spaces
    return /^[0-9+\-*/\s().]*$/.test(expr);
}

function evaluateExpression(expr) {
    // Simple arithmetic expression evaluation
    const tokens = expr.match(/(\d+|[-+*/()])/g);
    const outputQueue = [];
    const operatorStack = [];
    const precedence = { '+': 1, '-': 1, '*': 2, '/': 2 };

    tokens.forEach(token => {
        if (!isNaN(token)) {
            outputQueue.push(parseFloat(token));
        } else if (token in precedence) {
            while (operatorStack.length && precedence[operatorStack[operatorStack.length - 1]] >= precedence[token]) {
                outputQueue.push(operatorStack.pop());
            }
            operatorStack.push(token);
        } else if (token === '(') {
            operatorStack.push(token);
        } else if (token === ')') {
            while (operatorStack.length && operatorStack[operatorStack.length - 1] !== '(') {
                outputQueue.push(operatorStack.pop());
            }
            operatorStack.pop(); // Remove the '('
        }
    });

    while (operatorStack.length) {
        outputQueue.push(operatorStack.pop());
    }

    const evalStack = [];
    outputQueue.forEach(token => {
        if (typeof token === 'number') {
            evalStack.push(token);
        } else {
            const b = evalStack.pop();
            const a = evalStack.pop();
            switch (token) {
                case '+': evalStack.push(a + b); break;
                case '-': evalStack.push(a - b); break;
                case '*': evalStack.push(a * b); break;
                case '/': evalStack.push(a / b); break;
            }
        }
    });

    return evalStack[0];
}

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});