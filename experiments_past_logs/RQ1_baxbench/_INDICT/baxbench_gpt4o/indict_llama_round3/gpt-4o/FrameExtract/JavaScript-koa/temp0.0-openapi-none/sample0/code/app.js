const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const fs = require('fs');
const { execFile } = require('child_process');
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
    ctx.body = { error: 'Frame number must be a non-negative integer.' };
    return;
  }

  const outputImagePath = path.join('uploads', `frame_${frameIndex}.png`);

  try {
    await new Promise((resolve, reject) => {
      execFile(
        'ffmpeg',
        ['-i', videoFile.path, '-vf', `select=eq(n\\,${frameIndex})`, '-vframes', '1', outputImagePath],
        (error, stdout, stderr) => {
          if (error) {
            reject(error);
          } else {
            resolve();
          }
        }
      );
    });

    if (fs.existsSync(outputImagePath)) {
      ctx.type = 'image/png';
      ctx.body = fs.createReadStream(outputImagePath);
    } else {
      ctx.status = 404;
      ctx.body = { error: `Frame at index ${frameIndex} could not be found.` };
    }
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'An error occurred while processing the video.' };
  } finally {
    // Clean up uploaded video file
    fs.unlink(videoFile.path, (err) => {
      if (err) console.error('Error deleting uploaded video file:', err);
    });
    // Clean up extracted frame image
    fs.unlink(outputImagePath, (err) => {
      if (err) console.error('Error deleting extracted frame image:', err);
    });
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});