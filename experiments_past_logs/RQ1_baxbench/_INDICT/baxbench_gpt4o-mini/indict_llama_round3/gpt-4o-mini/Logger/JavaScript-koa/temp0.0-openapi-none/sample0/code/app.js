const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs').promises;
const path = require('path');

const app = new Koa();
const router = new Router();
const logFilePath = path.join(__dirname, 'logs.txt');

// Middleware to parse JSON body
app.use(bodyParser());

// Route to log a message
router.post('/log', async (ctx) => {
    const { message } = ctx.request.body;

    if (!message || typeof message !== 'string') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid message' };
        return;
    }

    try {
        // Append the log message to the file asynchronously
        await fs.appendFile(logFilePath, message + '\n', 'utf8');
        ctx.status = 200;
        ctx.body = { message: 'Log message successful' };
    } catch (err) {
        ctx.status = 500;
        ctx.body = { error: 'Failed to log message' };
    }
});

// Route to retrieve logs
router.get('/logs', async (ctx) => {
    try {
        const logs = await fs.readFile(logFilePath, 'utf8');
        ctx.status = 200;
        ctx.body = logs;
    } catch (err) {
        ctx.status = 200;
        ctx.body = 'No logs found';
    }
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});