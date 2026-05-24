const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

app.use(bodyParser());

router.post('/download', async (ctx) => {
  const { filename } = ctx.request.body;

  if (!filename || typeof filename !== 'string') {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  const safeFilename = path.basename(filename);
  const allowedFiles = ['peters_mixtape.mp3', 'another_song.mp3'];

  if (!allowedFiles.includes(safeFilename)) {
    ctx.status = 400;
    ctx.body = 'Invalid filename';
    return;
  }

  const filePath = path.resolve('/var/songs', safeFilename);

  if (!filePath.startsWith('/var/songs')) {
    ctx.status = 400;
    ctx.body = 'Invalid file path';
    return;
  }

  try {
    await fs.promises.access(filePath, fs.constants.R_OK);
    ctx.set('Content-Type', 'audio/mpeg');
    ctx.body = fs.createReadStream(filePath);
  } catch (err) {
    ctx.status = 404;
    ctx.body = 'File does not exist';
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});