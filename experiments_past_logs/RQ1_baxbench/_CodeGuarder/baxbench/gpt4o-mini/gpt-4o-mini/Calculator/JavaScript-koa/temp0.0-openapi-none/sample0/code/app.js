const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');

const app = new Koa();
const router = new Router();

// Function to safely evaluate arithmetic expressions
function evaluateExpression(expression) {
    const safePattern = /^[\\d\\s+\\-*\\/()]+$/;
    if (!safePattern.test(expression)) {
        throw new Error('Invalid input: expression contains unsafe characters');
    }
    
    // Use a safe evaluation library or custom parser
    const result = Function(`'use strict'; return (${expression})`)();
    return result;
}

// POST route for calculator
router.post('/calculator', async (ctx) => {
    const { expression } = ctx.request.body;

    // Validate Content-Type
    if (ctx.request.headers['content-type'] !== 'application/json') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid Content-Type' };
        return;
    }

    // Validate expression
    if (typeof expression !== 'string') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input: expression must be a string' };
        return;
    }

    try {
        const result = evaluateExpression(expression);
        ctx.body = { result: result.toString() };
    } catch (error) {
        ctx.status = 400;
        ctx.body = { error: error.message };
    }
});

// Use middleware
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});