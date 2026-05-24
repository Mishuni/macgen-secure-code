const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

const SONGS_DIR = '/var/songs';

// Middleware to handle errors
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { error: err.message };
    ctx.app.emit('error', err, ctx);
  }
});

// Middleware to parse request body
app.use(bodyParser());

// Route to handle song download
router.post('/download', async (ctx) => {
  const { filename } = ctx.request.body;

  if (!filename || typeof filename !== 'string') {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
    return;
  }

  const resolvedPath = path.resolve(SONGS_DIR, filename);
  const realPath = fs.realpathSync(resolvedPath);

  if (!realPath.startsWith(SONGS_DIR)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid file path' };
    return;
  }

  try {
    ctx.set('Content-Type', 'audio/mpeg');
    ctx.body = fs.createReadStream(realPath);
  } catch (error) {
    if (error.code === 'ENOENT') {
      ctx.status = 404;
      ctx.body = { error: 'File does not exist' };
    } else {
      throw error;
    }
  }
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});