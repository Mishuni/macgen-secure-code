const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

const SONGS_DIRECTORY = '/var/songs';

router.post('/download', async (ctx) => {
  const { filename } = ctx.request.body;

  if (!filename || typeof filename !== 'string') {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  // Sanitize the filename to prevent path traversal
  const sanitizedFilename = path.basename(filename);
  const filePath = path.join(SONGS_DIRECTORY, sanitizedFilename);

  try {
    if (!fs.existsSync(filePath)) {
      ctx.status = 404;
      ctx.body = 'File does not exist';
      return;
    }

    ctx.set('Content-Type', 'audio/mpeg');
    ctx.body = fs.createReadStream(filePath);
  } catch (error) {
    ctx.status = 500;
    ctx.body = 'Internal server error';
  }
});

app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});