const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

const LOG_FILE_PATH = path.join(__dirname, 'logs.txt');

// Middleware to handle errors and ensure secure error messages
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = 'Internal Server Error';
    console.error('Error occurred:', err.message);
  }
});

// Middleware to parse request bodies
app.use(bodyParser());

// POST /log endpoint to log a message
router.post('/log', async (ctx) => {
  const { message } = ctx.request.body;

  if (typeof message !== 'string' || message.trim() === '') {
    ctx.status = 400;
    ctx.body = 'Invalid message format';
    return;
  }

  // Securely handle file operations
  try {
    fs.appendFileSync(LOG_FILE_PATH, `${message}\n`, { encoding: 'utf8', mode: 0o600 });
    ctx.status = 200;
    ctx.body = 'Log message successful';
  } catch (err) {
    ctx.status = 500;
    ctx.body = 'Failed to log message';
    console.error('File write error:', err.message);
  }
});

// GET /logs endpoint to retrieve all logs
router.get('/logs', async (ctx) => {
  try {
    const logs = fs.readFileSync(LOG_FILE_PATH, { encoding: 'utf8' });
    ctx.status = 200;
    ctx.type = 'text/plain';
    ctx.body = logs;
  } catch (err) {
    ctx.status = 500;
    ctx.body = 'Failed to retrieve logs';
    console.error('File read error:', err.message);
  }
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start the Koa server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});