const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const util = require('util');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });
const execPromise = util.promisify(exec);

const PORT = 5000;

// Middleware for error handling
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { error: err.message };
    ctx.app.emit('error', err, ctx);
  }
});

// Define the /extract endpoint
router.post('/extract', upload.single('video'), async (ctx) => {
  const { frameNumber } = ctx.request.body;
  const videoFile = ctx.file;

  if (!videoFile || !frameNumber) {
    ctx.status = 400;
    ctx.body = { error: 'Video file and frame number are required.' };
    return;
  }

  const frameIndex = parseInt(frameNumber, 10);
  if (isNaN(frameIndex) || frameIndex < 0) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid frame number.' };
    return;
  }

  const outputFilePath = path.join('uploads', `frame-${Date.now()}.png`);

  try {
    // Extract frame using ffmpeg
    await execPromise(`ffmpeg -i ${videoFile.path} -vf "select=eq(n\\,${frameIndex})" -vframes 1 ${outputFilePath}`);

    // Check if the frame was extracted
    if (!fs.existsSync(outputFilePath)) {
      ctx.status = 404;
      ctx.body = { error: `Frame at index ${frameIndex} could not be found.` };
      return;
    }

    // Send the extracted frame as response
    ctx.type = 'image/png';
    ctx.body = fs.createReadStream(outputFilePath);
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Failed to extract frame.' };
  } finally {
    // Clean up temporary files
    fs.unlink(videoFile.path, (err) => {
      if (err) console.error('Failed to delete video file:', err);
    });
    fs.unlink(outputFilePath, (err) => {
      if (err) console.error('Failed to delete output file:', err);
    });
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});