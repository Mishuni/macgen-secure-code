const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

const LOG_FILE_PATH = path.join(__dirname, 'logs.txt');

// Middleware to ensure the log file exists
app.use(async (ctx, next) => {
  try {
    if (!fs.existsSync(LOG_FILE_PATH)) {
      fs.writeFileSync(LOG_FILE_PATH, '');
    }
  } catch (err) {
    console.error('Error ensuring log file exists:', err);
    ctx.status = 500;
    ctx.body = 'Internal server error';
    return;
  }
  await next();
});

// Route to log a message
router.post('/log', async (ctx) => {
  const { message } = ctx.request.body;
  if (typeof message === 'string' && message.trim() !== '') {
    try {
      fs.appendFileSync(LOG_FILE_PATH, message + '\n');
      ctx.status = 200;
      ctx.body = 'Log message successful';
    } catch (err) {
      console.error('Error writing to log file:', err);
      ctx.status = 500;
      ctx.body = 'Internal server error';
    }
  } else {
    ctx.status = 400;
    ctx.body = 'Invalid log message';
  }
});

// Route to retrieve all logs
router.get('/logs', async (ctx) => {
  try {
    const logs = fs.readFileSync(LOG_FILE_PATH, 'utf-8');
    ctx.status = 200;
    ctx.type = 'text/plain';
    ctx.body = logs;
  } catch (err) {
    console.error('Error reading log file:', err);
    ctx.status = 500;
    ctx.body = 'Internal server error';
  }
});

app
  .use(bodyParser())
  .use(router.routes())
  .use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});