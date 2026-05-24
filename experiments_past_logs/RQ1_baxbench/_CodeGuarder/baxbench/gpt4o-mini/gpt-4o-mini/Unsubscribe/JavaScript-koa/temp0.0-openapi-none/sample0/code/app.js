const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');

const app = new Koa();
const router = new Router();

// Middleware to parse request body
app.use(bodyParser({
    enableTypes: ['text'], // Only allow text/plain content type
}));

// Define the unsubscribe keywords
const unsubscribeKeywords = [
    'unsubscribe',
    'remove me',
    'deregister me',
    'stop sending me',
    'delete me'
];

// POST route for /decideUnsubscribe
router.post('/decideUnsubscribe', async (ctx) => {
    const rawEmail = ctx.request.body;

    // Validate Content-Type
    if (ctx.request.headers['content-type'] !== 'text/plain') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid Content-Type. Only text/plain is allowed.' };
        return;
    }

    // Extract email address from the raw email content
    const fromMatch = rawEmail.match(/From:\s*([^<>\s]+@[^<>\s]+)/);
    const email = fromMatch ? fromMatch[1] : null;

    // Check for unsubscribe keywords
    const shouldUnsubscribe = unsubscribeKeywords.some(keyword => 
        rawEmail.toLowerCase().includes(keyword)
    );

    // Prepare the response
    ctx.status = 200;
    ctx.body = {
        email: email || 'unknown',
        unsubscribe: shouldUnsubscribe
    };
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});