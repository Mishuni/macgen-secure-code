const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { Parser } = require('expr-eval'); // Using expr-eval for safe expression evaluation

const app = new Koa();
const router = new Router();

// Middleware for security headers
app.use(async (ctx, next) => {
    ctx.set('X-Content-Type-Options', 'nosniff');
    ctx.set('X-Frame-Options', 'DENY');
    ctx.set('Content-Security-Policy', "default-src 'self'");
    ctx.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains'); // HSTS
    ctx.set('X-XSS-Protection', '1; mode=block'); // XSS Protection
    ctx.set('Referrer-Policy', 'no-referrer'); // Referrer Policy
    await next();
});

router.post('/calculator', async (ctx) => {
    const { expression } = ctx.request.body;

    // Validate input
    if (typeof expression !== 'string' || !/^[\d\s\+\-\*\/\(\)]+$/.test(expression)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    // Limit input length
    if (expression.length > 100) {
        ctx.status = 400;
        ctx.body = { error: 'Input too long' };
        return;
    }

    try {
        // Evaluate the expression safely using expr-eval
        const result = Parser.evaluate(expression);
        ctx.body = { result: result.toString() };
    } catch (error) {
        // Log the error internally (not shown here for brevity)
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
    }
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
});