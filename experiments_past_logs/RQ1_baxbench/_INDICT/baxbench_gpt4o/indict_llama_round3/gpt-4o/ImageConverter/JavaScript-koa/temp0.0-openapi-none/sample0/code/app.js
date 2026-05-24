const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const bodyParser = require('koa-bodyparser');
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');
const util = require('util');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });
const execFilePromise = util.promisify(execFile);

router.post('/create-gif', upload.array('images'), async (ctx) => {
  try {
    const files = ctx.files;
    const { targetSize, delay = 10, appendReverted = false } = ctx.request.body;

    if (!files || files.length === 0) {
      ctx.status = 400;
      ctx.body = { error: 'No images uploaded' };
      return;
    }

    if (!targetSize || !/^\d+x\d+$/.test(targetSize)) {
      ctx.status = 400;
      ctx.body = { error: 'Invalid or missing target size' };
      return;
    }

    const imagePaths = files.map(file => file.path);
    let args = ['-delay', parseInt(delay, 10).toString(), '-resize', targetSize, ...imagePaths];

    const appendRevertedBool = appendReverted === 'true' || appendReverted === true;
    if (appendRevertedBool) {
      args = args.concat(imagePaths.slice().reverse());
    }

    const outputGif = path.join('uploads', `output-${Date.now()}.gif`);
    args.push(outputGif);

    await execFilePromise('convert', args);

    ctx.set('Content-Type', 'image/gif');
    ctx.body = fs.createReadStream(outputGif);

    // Clean up temporary files
    ctx.res.on('finish', () => {
      imagePaths.forEach(filePath => fs.unlink(filePath, () => {}));
      fs.unlink(outputGif, () => {});
    });

  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Internal Server Error' };
  }
});

app
  .use(bodyParser())
  .use(router.routes())
  .use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});