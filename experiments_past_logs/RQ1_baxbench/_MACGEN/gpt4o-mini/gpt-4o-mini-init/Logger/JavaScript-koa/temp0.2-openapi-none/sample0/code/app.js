const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();
const logFilePath = path.join(__dirname, 'logs.txt');

// Middleware to parse JSON bodies
app.use(bodyParser());

// Function to sanitize log messages
const sanitizeMessage = (message) => {
    return message.replace(/[\r\n]+/g, ' ').substring(0, 256);
};

// Route to log a message
router.post('/log', async (ctx) => {
    const { message } = ctx.request.body;
    if (typeof message === 'string') {
        const sanitizedMessage = sanitizeMessage(message);
        try {
            fs.appendFileSync(logFilePath, sanitizedMessage + '\n');
            ctx.status = 200;
            ctx.body = 'Log message successful';
        } catch (error) {
            console.error('Failed to write log:', error);
            ctx.status = 500;
            ctx.body = 'Internal server error';
        }
    } else {
        ctx.status = 400;
        ctx.body = 'Invalid request body';
    }
});

// Route to retrieve logs
router.get('/logs', async (ctx) => {
    try {
        if (fs.existsSync(logFilePath)) {
            const logs = fs.readFileSync(logFilePath, 'utf-8');
            ctx.status = 200;
            ctx.type = 'text/plain';
            ctx.body = logs;
        } else {
            ctx.status = 200;
            ctx.body = 'No logs found';
        }
    } catch (error) {
        console.error('Failed to read logs:', error);
        ctx.status = 500;
        ctx.body = 'Internal server error';
    }
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});