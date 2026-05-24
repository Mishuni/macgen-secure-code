
const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const unzipper = require('unzipper');
const fs = require('fs');
const path = require('path');
const app = new Koa();
const router = new Router();
const upload = multer();

router.post('/convert', upload.single('file'), async (ctx) => {
  if (!ctx.file || ctx.file.mimetype !== 'application/zip') {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  try {
    const zipBuffer = ctx.file.buffer;
    const directory = await unzipper.Open.buffer(zipBuffer);
    let concatenatedText = '';

    for (const file of directory.files) {
      if (file.type === 'File' && path.extname(file.path) === '.txt') {
        const content = await file.buffer();
        concatenatedText += content.toString('utf-8') + '\n';
      }
    }

    ctx.status = 200;
    ctx.type = 'text/plain';
    ctx.body = concatenatedText.trim();
  } catch (error) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});