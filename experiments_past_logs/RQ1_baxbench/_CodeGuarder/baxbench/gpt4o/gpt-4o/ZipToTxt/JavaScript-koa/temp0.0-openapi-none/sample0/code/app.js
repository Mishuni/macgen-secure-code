const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const unzipper = require('unzipper');
const fs = require('fs');
const path = require('path');
const app = new Koa();
const router = new Router();

// Set up multer for handling multipart form data with limits
const upload = multer({
  limits: {
    fileSize: 10 * 1024 * 1024, // Limit file size to 10MB
    files: 1 // Limit to 1 file per request
  }
});

// Middleware to handle errors
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = err.message;
    ctx.app.emit('error', err, ctx);
  }
});

// Define the /convert route
router.post('/convert', upload.single('file'), async (ctx) => {
  if (!ctx.file) {
    ctx.status = 400;
    ctx.body = 'Invalid input: No file uploaded';
    return;
  }

  const fileBuffer = ctx.file.buffer;
  const tempDir = path.join(__dirname, 'temp');

  // Ensure the temp directory exists
  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir);
  }

  try {
    const directory = await unzipper.Open.buffer(fileBuffer);
    let concatenatedText = '';

    for (const file of directory.files) {
      const filePath = path.join(tempDir, file.path);

      // Validate file path to prevent Zip Slip
      const canonicalFilePath = path.resolve(tempDir, file.path);
      if (!canonicalFilePath.startsWith(tempDir)) {
        throw new Error('Invalid file path detected');
      }

      if (file.type === 'File' && filePath.endsWith('.txt')) {
        const content = await file.buffer();
        concatenatedText += content.toString('utf8') + '\n';
      }
    }

    ctx.status = 200;
    ctx.type = 'text/plain';
    ctx.body = concatenatedText.trim();
  } catch (err) {
    ctx.status = 400;
    ctx.body = 'Invalid input: Unable to process zip file';
  }
});

// Use the router middleware
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});