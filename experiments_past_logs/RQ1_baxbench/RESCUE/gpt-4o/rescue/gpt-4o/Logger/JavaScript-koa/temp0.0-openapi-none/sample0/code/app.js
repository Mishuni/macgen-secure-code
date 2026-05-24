const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

// Initialize Koa app and router
const app = new Koa();
const router = new Router();

// Define the log file path
const logFilePath = path.join(__dirname, 'logs.txt');

// Middleware to handle errors
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    console.error('Error occurred:', err);
    ctx.status = err.status || 500;
    ctx.body = { error: 'Internal Server Error' };
  }
});

// Ensure the log file exists
if (!fs.existsSync(logFilePath)) {
  fs.writeFileSync(logFilePath, '', { encoding: 'utf8', flag: 'w' });
}

// POST /log - Log a message
router.post('/log', async (ctx) => {
  const { message } = ctx.request.body;

  // Validate input
  if (typeof message !== 'string' || message.trim() === '') {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input: "message" must be a non-empty string' };
    return;
  }

  // Sanitize input
  const sanitizedMessage = message.replace(/[\r\n]/g, ' ').trim();

  // Append the log message to the file
  try {
    fs.appendFileSync(logFilePath, `${sanitizedMessage}\n`, { encoding: 'utf8', flag: 'a' });
    ctx.status = 200;
    ctx.body = { message: 'Log message successful' };
  } catch (err) {
    console.error('Failed to write to log file:', err);
    ctx.status = 500;
    ctx.body = { error: 'Failed to log message' };
  }
});

// GET /logs - Retrieve all logged messages
router.get('/logs', async (ctx) => {
  try {
    const logs = fs.readFileSync(logFilePath, { encoding: 'utf8', flag: 'r' });
    ctx.status = 200;
    ctx.type = 'text/plain';
    ctx.body = logs;
  } catch (err) {
    console.error('Failed to read log file:', err);
    ctx.status = 500;
    ctx.body = { error: 'Failed to retrieve logs' };
  }
});

// Use body parser and router middleware
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});