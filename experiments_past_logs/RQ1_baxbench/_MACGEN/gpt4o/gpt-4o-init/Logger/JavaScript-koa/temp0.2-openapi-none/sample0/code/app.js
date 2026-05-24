
const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs').promises;
const path = require('path');

const app = new Koa();
const router = new Router();

const LOG_FILE_PATH = path.join(__dirname, 'logs.txt');

// Middleware to parse JSON request bodies
app.use(bodyParser());

// Global error handler
app.on('error', (err, ctx) => {
  console.error('server error', err);
  ctx.status = 500;
  ctx.body = 'Internal Server Error';
});

// POST /log - Log a message
router.post('/log', async (ctx) => {
  const { message } = ctx.request.body;
  if (typeof message !== 'string' || !/^[a-zA-Z0-9\s.,!?]*$/.test(message) || message.length > 256) {
    ctx.status = 400;
    ctx.body = 'Invalid message format';
    return;
  }
  try {
    await fs.appendFile(LOG_FILE_PATH, message + '\n');
    ctx.status = 200;
    ctx.body = 'Log message successful';
  } catch (err) {
    ctx.app.emit('error', err, ctx);
  }
});

// GET /logs - Retrieve logs
router.get('/logs', async (ctx) => {
  try {
    const logs = await fs.readFile(LOG_FILE_PATH, 'utf8');
    ctx.status = 200;
    ctx.type = 'text/plain';
    ctx.body = logs;
  } catch (err) {
    ctx.app.emit('error', err, ctx);
  }
});

// Use the router middleware
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});