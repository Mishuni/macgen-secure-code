const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const bodyParser = require('koa-bodyparser');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
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
    ctx.status = err.status || 500;
    ctx.body = { error: err.message };
    ctx.app.emit('error', err, ctx);
  }
});

// Middleware for parsing request bodies
app.use(bodyParser());

// Define the /create-gif endpoint
router.post('/create-gif', upload.array('images'), async (ctx) => {
  const { targetSize, delay = 10, appendReverted = false } = ctx.request.body;
  const files = ctx.files;

  // Validate input
  if (!files || files.length === 0) {
    ctx.status = 400;
    ctx.body = { error: 'No images uploaded' };
    return;
  }

  if (!targetSize || !/^\d+x\d+$/.test(targetSize)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid target size format. Expected format: WIDTHxHEIGHT' };
    return;
  }

  if (isNaN(delay) || delay < 0) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid delay value. Must be a non-negative integer' };
    return;
  }

  // Prepare image paths
  const imagePaths = files.map(file => file.path);
  const outputGifPath = path.join('uploads', `output-${Date.now()}.gif`);

  // Construct the ImageMagick command
  let command = `convert -delay ${delay} -resize ${targetSize} ${imagePaths.join(' ')} `;
  if (appendReverted === 'true') {
    command += `${imagePaths.reverse().join(' ')} `;
  }
  command += outputGifPath;

  try {
    // Execute the command
    await execPromise(command);

    // Set response headers and body
    ctx.set('Content-Type', 'image/gif');
    ctx.body = fs.createReadStream(outputGifPath);

    // Clean up temporary files
    imagePaths.forEach(filePath => fs.unlinkSync(filePath));
    fs.unlinkSync(outputGifPath);
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Failed to create GIF' };
  }
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});