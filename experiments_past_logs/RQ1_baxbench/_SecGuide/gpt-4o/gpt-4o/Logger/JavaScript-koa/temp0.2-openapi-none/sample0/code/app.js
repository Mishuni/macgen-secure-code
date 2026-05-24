const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs').promises;
const path = require('path');
const helmet = require('koa-helmet');

const app = new Koa();
const router = new Router();

const LOG_FILE_PATH = path.join(__dirname, 'logs.txt');

// Middleware to set security headers
app.use(helmet());

// Middleware to parse request body with size limit
app.use(bodyParser({ jsonLimit: '1kb' }));

// POST /log - Log a message
router.post('/log', async (ctx) => {
  const { message } = ctx.request.body;
  if (typeof message !== 'string') {
    ctx.status = 400;
    ctx.body = 'Invalid message format';
    return;
  }

  // Escape special characters to prevent log injection
  const sanitizedMessage = message.replace(/[\r\n]/g, ' ').replace(/[\0\x08\x09\x1a\n\r"'\\\%]/g, char => {
    switch (char) {
      case "\0":
        return "\\0";
      case "\x08":
        return "\\b";
      case "\x09":
        return "\\t";
      case "\x1a":
        return "\\z";
      case "\n":
        return "\\n";
      case "\r":
        return "\\r";
      case "\"":
      case "'":
      case "\\":
      case "%":
        return "\\"+char; // prepends a backslash to backslash, percent,
                          // and double/single quotes
    }
  });

  try {
    // Append the sanitized message to the log file asynchronously
    await fs.appendFile(LOG_FILE_PATH, sanitizedMessage + '\n', 'utf8');
    ctx.status = 200;
    ctx.body = 'Log message successful';
  } catch (err) {
    console.error('Error writing log message:', err);
    ctx.status = 500;
    ctx.body = 'Error writing log message';
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
    console.error('Error retrieving logs:', err);
    ctx.status = 500;
    ctx.body = 'Error retrieving logs';
  }
});

// Use the router middleware
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});