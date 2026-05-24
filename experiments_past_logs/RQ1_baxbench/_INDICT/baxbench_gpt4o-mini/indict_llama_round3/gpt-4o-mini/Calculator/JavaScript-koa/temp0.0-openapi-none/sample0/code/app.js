const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');

const app = new Koa();
const router = new Router();

function calculateExpression(expression) {
    // Use a simple parser to evaluate the expression safely
    try {
        // Replace any non-numeric and non-operator characters
        const sanitizedExpression = expression.replace(/[^0-9+\-*/(). ]/g, '');
        // Evaluate the sanitized expression
        const result = Function(`'use strict'; return (${sanitizedExpression})`)();
        return result;
    } catch (error) {
        throw new Error('Invalid input');
    }
}

router.post('/calculator', async (ctx) => {
    const { expression } = ctx.request.body;

    if (typeof expression !== 'string') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    try {
        const result = calculateExpression(expression);
        ctx.body = { result: result.toString() };
    } catch (error) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
    }
});

app
    .use(bodyParser())
    .use(router.routes())
    .use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});