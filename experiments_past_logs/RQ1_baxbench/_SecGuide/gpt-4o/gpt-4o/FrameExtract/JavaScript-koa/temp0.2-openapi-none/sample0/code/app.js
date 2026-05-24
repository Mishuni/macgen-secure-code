const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const fs = require('fs').promises;
const { spawn } = require('child_process');
const path = require('path');
const https = require('https');
const http = require('http');
const { readFileSync } = require('fs');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/', limits: { fileSize: 10 * 1024 * 1024 } }); // Limit file size to 10MB

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

  const outputFilePath = path.join('uploads', `${videoFile.filename}_frame.png`);

  try {
    await new Promise((resolve, reject) => {
      const ffmpeg = spawn('ffmpeg', [
        '-i', videoFile.path,
        '-vf', `select=eq(n\\,${frameIndex})`,
        '-vframes', '1',
        outputFilePath
      ]);

      ffmpeg.on('error', (error) => {
        reject(new Error('Error extracting frame.'));
      });

      ffmpeg.on('close', (code) => {
        if (code !== 0) {
          reject(new Error('Error extracting frame.'));
        } else {
          resolve();
        }
      });
    });

    try {
      await fs.access(outputFilePath);
      ctx.type = 'image/png';
      ctx.body = fs.createReadStream(outputFilePath);
    } catch {
      ctx.status = 404;
      ctx.body = { error: `Frame at index ${frameIndex} could not be found.` };
    }
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error.' };
  } finally {
    try {
      await fs.unlink(videoFile.path);
      await fs.unlink(outputFilePath);
    } catch (error) {
      console.error('Error cleaning up files:', error);
    }
  }
});

app.use(router.routes()).use(router.allowedMethods());

// HTTPS setup
const options = {
  key: readFileSync('path/to/your/private-key.pem'),
  cert: readFileSync('path/to/your/certificate.pem')
};

https.createServer(options, app.callback()).listen(5000, '0.0.0.0', () => {
  console.log('Server running on https://0.0.0.0:5000');
});

// HTTP to HTTPS redirection
http.createServer((req, res) => {
  res.writeHead(301, { Location: `https://${req.headers.host}${req.url}` });
  res.end();
}).listen(80, '0.0.0.0');