const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const unzipper = require('unzipper');
const path = require('path');
const app = new Koa();
const router = new Router();
const upload = multer();

// Middleware to limit file size to prevent denial of service
const fileSizeLimit = 10 * 1024 * 1024; // 10 MB

router.post('/convert', upload.single('file'), async (ctx) => {
  if (!ctx.file) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  if (ctx.file.size > fileSizeLimit) {
    ctx.status = 400;
    ctx.body = 'File size exceeds limit';
    return;
  }

  try {
    const zipBuffer = ctx.file.buffer;
    const directory = await unzipper.Open.buffer(zipBuffer);
    let combinedText = '';

    for (const file of directory.files) {
      if (file.type === 'File' && path.extname(file.path) === '.txt') {
        // Validate file path to prevent Zip Slip
        const sanitizedPath = path.normalize(file.path).replace(/^(\.\.(\/|\\|$))+/, '');
        if (sanitizedPath !== file.path) {
          ctx.status = 400;
          ctx.body = 'Invalid file path detected';
          return;
        }

        const content = await file.buffer();
        combinedText += content.toString() + '\n';
      }
    }

    ctx.status = 200;
    ctx.type = 'text/plain';
    ctx.body = combinedText.trim();
  } catch (error) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});