const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const bodyParser = require('koa-bodyparser');
const sharp = require('sharp');
const path = require('path');
const fs = require('fs').promises;
const mime = require('mime-types');

const app = new Koa();
const router = new Router();
const upload = multer({
  dest: 'uploads/',
  limits: {
    fileSize: 5 * 1024 * 1024, // Limit file size to 5MB
  },
  fileFilter: (req, file, cb) => {
    const mimeType = mime.lookup(file.originalname);
    if (mimeType === 'image/jpeg' || mimeType === 'image/png') {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only JPEG and PNG are allowed.'));
    }
  },
});

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
      ctx.body = { error: 'Invalid target size format' };
      return;
    }

    const delayInt = parseInt(delay, 10);
    if (isNaN(delayInt) || delayInt <= 0) {
      ctx.status = 400;
      ctx.body = { error: 'Invalid delay value' };
      return;
    }

    const [width, height] = targetSize.split('x').map(Number);
    if (isNaN(width) || isNaN(height) || width <= 0 || height <= 0) {
      ctx.status = 400;
      ctx.body = { error: 'Invalid target size dimensions' };
      return;
    }

    const imageBuffers = await Promise.all(files.map(file => fs.readFile(file.path)));
    const processedImages = await Promise.all(imageBuffers.map(buffer => sharp(buffer).resize(width, height).toBuffer()));

    if (appendReverted === 'true') {
      processedImages.push(...processedImages.slice().reverse());
    }

    const outputFilePath = path.join('uploads', `output-${Date.now()}.gif`);
    await sharp({
      create: {
        width: width,
        height: height,
        channels: 4,
        background: { r: 0, g: 0, b: 0, alpha: 0 }
      }
    })
    .gif({ delay: delayInt })
    .composite(processedImages.map((buffer, index) => ({ input: buffer, top: 0, left: 0, delay: delayInt })))
    .toFile(outputFilePath);

    ctx.set('Content-Type', 'image/gif');
    ctx.body = fs.createReadStream(outputFilePath);

    // Clean up uploaded files
    await Promise.all(files.map(file => fs.unlink(file.path)));
    await fs.unlink(outputFilePath);

  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Internal Server Error' };
    console.error('Error processing request:', error);
  }
});

app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});