const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs').promises; // Use promises for async file operations
const path = require('path');
const sanitizeHtml = require('sanitize-html'); // Sanitize input to prevent log injection
const rateLimit = require('koa-ratelimit'); // Rate limiting middleware

const app = new Koa();
const router = new Router();
const logFilePath = process.env.LOG_FILE_PATH || path.join(__dirname, 'logs.txt'); // Use environment variable for log file path

// Middleware to handle JSON body parsing
app.use(bodyParser());

// Rate limiting middleware
app.use(rateLimit({
    driver: 'memory',
    db: new Map(),
    duration: 60000, // 1 minute
    errorMessage: 'Too many requests, please try again later.',
    id: (ctx) => ctx.ip, // Use IP address as identifier
    max: 100, // Limit each IP to 100 requests per minute
    disableHeader: false, // Enable rate limit headers
}));

// Route to log a message
router.post('/log', async (ctx) => {
    const { message } = ctx.request.body;

    if (typeof message !== 'string') {
        ctx.status = 400;
        ctx.body = { error: 'Message must be a string' };
        return;
    }

    // Validate message length
    if (message.length > 1000) {
        ctx.status = 400;
        ctx.body = { error: 'Message is too long' };
        return;
    }

    // Sanitize the message to prevent log injection
    const sanitizedMessage = sanitizeHtml(message, {
        allowedTags: [],
        allowedAttributes: {}
    });

    // Append the log message to the file asynchronously
    try {
        await fs.appendFile(logFilePath, sanitizedMessage + '\n', 'utf8');
        ctx.status = 200;
        ctx.body = { message: 'Log message successful' };
    } catch (error) {
        ctx.status = 500;
        ctx.body = { error: 'Failed to write log message' };
    }
});

// Route to retrieve logs
router.get('/logs', async (ctx) => {
    try {
        const logs = await fs.readFile(logFilePath, 'utf8');
        ctx.status = 200;
        ctx.body = logs;
    } catch (error) {
        ctx.status = 500; // Return 500 for server error
        ctx.body = { error: 'Failed to retrieve logs' }; // Generic error message
    }
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// CORS configuration (if needed)
app.use(async (ctx, next) => {
    ctx.set('Access-Control-Allow-Origin', '*'); // Adjust as necessary for security
    ctx.set('Access-Control-Allow-Methods', 'GET, POST');
    ctx.set('Access-Control-Allow-Headers', 'Content-Type');
    await next();
});

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});