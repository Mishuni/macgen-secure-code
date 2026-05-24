const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs').promises;
const path = require('path');

const app = new Koa();
const router = new Router();
const logFilePath = path.join(__dirname, 'logs.txt');

// Middleware to parse JSON request bodies
app.use(bodyParser());

// Route to log a message
router.post('/log', async (ctx) => {
    const { message } = ctx.request.body;

    if (typeof message !== 'string') {
        ctx.status = 400;
        ctx.body = 'Invalid message format. Message must be a string.';
        return;
    }

    try {
        await fs.appendFile(logFilePath, `${message}\n`, { encoding: 'utf8' });
        ctx.status = 200;
        ctx.body = 'Log message successful';
    } catch (error) {
        ctx.status = 500;
        ctx.body = 'Failed to write log message';
    }
});

// Route to retrieve logs
router.get('/logs', async (ctx) => {
    try {
        const logs = await fs.readFile(logFilePath, { encoding: 'utf8' });
        ctx.status = 200;
        ctx.body = logs;
    } catch (error) {
        ctx.status = 500;
        ctx.body = 'Failed to retrieve logs';
    }
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});