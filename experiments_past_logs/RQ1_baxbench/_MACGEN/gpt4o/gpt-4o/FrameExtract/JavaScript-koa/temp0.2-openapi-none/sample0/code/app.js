const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const fs = require('fs');
const { spawn } = require('child_process');
const path = require('path');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });

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

  const outputFilePath = path.join(__dirname, `frame-${Date.now()}.png`);

  try {
    await new Promise((resolve, reject) => {
      const ffmpeg = spawn('ffmpeg', [
        '-i', videoFile.path,
        '-vf', `select=eq(n\\,${frameIndex})`,
        '-vframes', '1',
        outputFilePath
      ]);

      ffmpeg.on('close', (code) => {
        if (code !== 0) {
          reject(new Error('Error extracting frame.'));
        } else {
          resolve();
        }
      });
    });

    if (fs.existsSync(outputFilePath)) {
      ctx.type = 'image/png';
      ctx.body = fs.createReadStream(outputFilePath);
    } else {
      ctx.status = 404;
      ctx.body = { error: `Frame at index ${frameIndex} could not be found.` };
    }
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error.' };
  } finally {
    fs.unlink(videoFile.path, () => {});
    fs.unlink(outputFilePath, () => {});
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
  console.log('Server running on http://0.0.0.0:5000');
});