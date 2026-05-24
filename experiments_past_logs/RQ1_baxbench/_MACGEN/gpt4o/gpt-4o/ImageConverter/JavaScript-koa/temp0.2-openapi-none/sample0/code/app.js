const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
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

    // Input validation
    if (!files || files.length === 0) {
      ctx.status = 400;
      ctx.body = { error: 'No images uploaded' };
      return;
    }

    if (!/^\d+x\d+$/.test(targetSize)) {
      ctx.status = 400;
      ctx.body = { error: 'Invalid target size format' };
      return;
    }

    const delayInt = parseInt(delay, 10);
    if (isNaN(delayInt) || delayInt <= 0) {
      ctx.status = 400;
      ctx.body = { error: 'Invalid delay value' };
      return;
    }

    const appendRevertedBool = appendReverted === 'true';

    const inputFiles = files.map(file => file.path);
    const outputFile = path.join('uploads', `output-${Date.now()}.gif`);

    let args = ['-delay', delayInt.toString(), '-resize', targetSize, ...inputFiles];

    if (appendRevertedBool) {
      args = args.concat(inputFiles.slice().reverse());
    }

    args.push(outputFile);

    await execFilePromise('convert', args);

    ctx.type = 'image/gif';
    ctx.body = fs.createReadStream(outputFile);

    // Clean up temporary files
    ctx.res.on('finish', () => {
      inputFiles.forEach(file => fs.unlink(file, () => {}));
      fs.unlink(outputFile, () => {});
    });

  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Internal Server Error' };
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});