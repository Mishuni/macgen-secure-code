const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();
const logFilePath = path.join(__dirname, 'logs.txt');

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = 'Internal Server Error';
        console.error(err);
    }
});

// Log a message
router.post('/log', async (ctx) => {
    const { message } = ctx.request.body;

    // Validate input
    if (typeof message !== 'string' || message.trim() === '') {
        ctx.status = 400;
        ctx.body = 'Invalid message';
        return;
    }

    // Sanitize the message
    const sanitizedMessage = message.replace(/[\r\n]+/g, ' ').replace(/[^a-zA-Z0-9 .,!?"'()]/g, '');

    // Append the log message to the file
    fs.appendFileSync(logFilePath, sanitizedMessage + '\n', { encoding: 'utf8' });

    ctx.status = 200;
    ctx.body = 'Log message successful';
});

// Retrieve logs
router.get('/logs', async (ctx) => {
    try {
        const logs = fs.readFileSync(logFilePath, { encoding: 'utf8' });
        ctx.status = 200;
        ctx.type = 'text/plain';
        ctx.body = logs;
    } catch (err) {
        ctx.status = 500;
        ctx.body = 'Unable to retrieve logs';
        console.error(err);
    }
});

// Use body parser and router
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});