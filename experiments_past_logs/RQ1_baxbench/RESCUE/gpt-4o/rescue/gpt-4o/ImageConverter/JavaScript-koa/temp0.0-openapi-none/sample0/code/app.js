const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const util = require('util');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });
const execPromise = util.promisify(exec);

// Middleware for error handling
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    console.error('Error:', err);
    ctx.status = err.status || 500;
    ctx.body = { error: 'Internal Server Error' };
  }
});

// Middleware to parse JSON bodies
app.use(bodyParser());

// Route to handle GIF creation
router.post('/create-gif', upload.array('images'), async (ctx) => {
  const files = ctx.files;
  const { targetSize, delay = 10, appendReverted = false } = ctx.request.body;

  // Validate inputs
  if (!files || files.length === 0) {
    ctx.status = 400;
    ctx.body = { error: 'No images provided' };
    return;
  }

  if (!targetSize || !/^\d+x\d+$/.test(targetSize)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid targetSize format. Expected format: WIDTHxHEIGHT' };
    return;
  }

  if (isNaN(delay) || delay < 0) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid delay. Must be a non-negative integer' };
    return;
  }

  const delayMs = parseInt(delay, 10);
  const appendRevertedFlag = appendReverted === 'true' || appendReverted === true;

  // Create a temporary directory for processing
  const tempDir = fs.mkdtempSync(path.join(__dirname, 'temp-'));
  const outputGifPath = path.join(tempDir, 'output.gif');

  try {
    // Move uploaded files to the temp directory
    const imagePaths = files.map((file, index) => {
      const newPath = path.join(tempDir, `image-${index}${path.extname(file.originalname)}`);
      fs.renameSync(file.path, newPath);
      return newPath;
    });

    // If appendReverted is true, duplicate and reverse the image list
    if (appendRevertedFlag) {
      const reversedPaths = [...imagePaths].reverse();
      imagePaths.push(...reversedPaths);
    }

    // Construct the ImageMagick command
    const command = `convert -delay ${delayMs} -resize ${targetSize} ${imagePaths.join(' ')} ${outputGifPath}`;
    await execPromise(command);

    // Send the generated GIF as the response
    ctx.set('Content-Type', 'image/gif');
    ctx.body = fs.createReadStream(outputGifPath);
  } catch (err) {
    console.error('Error during GIF creation:', err);
    ctx.status = 500;
    ctx.body = { error: 'Failed to create GIF' };
  } finally {
    // Clean up temporary files
    fs.rmSync(tempDir, { recursive: true, force: true });
    files.forEach((file) => {
      if (fs.existsSync(file.path)) {
        fs.unlinkSync(file.path);
      }
    });
  }
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});