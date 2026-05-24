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

// Ensure the uploads and output directories exist
const UPLOAD_DIR = path.resolve(__dirname, 'uploads');
const OUTPUT_DIR = path.resolve(__dirname, 'output');
if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR);
if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR);

// Sanitize filename to prevent directory traversal
function sanitizeFilename(filename) {
  return path.basename(filename).replace(/[^a-zA-Z0-9._-]/g, '');
}

// Route to handle frame extraction
router.post('/extract', upload.single('video'), async (ctx) => {
  try {
    const { frameNumber, videoFileName } = ctx.request.body;

    // Validate inputs
    if (!ctx.file || !frameNumber || !videoFileName) {
      ctx.status = 400;
      ctx.body = { error: 'Missing required fields: video, frameNumber, or videoFileName' };
      return;
    }

    const sanitizedFilename = sanitizeFilename(videoFileName);
    const frameIndex = parseInt(frameNumber, 10);

    if (isNaN(frameIndex) || frameIndex < 0) {
      ctx.status = 400;
      ctx.body = { error: 'Invalid frameNumber. It must be a non-negative integer.' };
      return;
    }

    const uploadedFilePath = path.join(UPLOAD_DIR, ctx.file.filename);
    const outputFilePath = path.join(OUTPUT_DIR, `${sanitizedFilename}_frame_${frameIndex}.png`);

    // Use ffmpeg to extract the frame
    const ffmpegCommand = `ffmpeg -i "${uploadedFilePath}" -vf "select=eq(n\\,${frameIndex})" -vframes 1 "${outputFilePath}"`;
    try {
      await execPromise(ffmpegCommand);

      // Check if the output file was created
      if (!fs.existsSync(outputFilePath)) {
        ctx.status = 404;
        ctx.body = { error: `Frame at index ${frameIndex} could not be found.` };
        return;
      }

      // Send the extracted frame as a response
      ctx.set('Content-Type', 'image/png');
      ctx.body = fs.createReadStream(outputFilePath);
    } catch (error) {
      ctx.status = 500;
      ctx.body = { error: 'An error occurred while processing the video.' };
    } finally {
      // Clean up uploaded file
      fs.unlinkSync(uploadedFilePath);
    }
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'An unexpected error occurred.' };
  }
});

// Register routes and start the server
app.use(router.routes()).use(router.allowedMethods());

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});