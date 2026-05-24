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

// Define the /convert route
router.post('/convert', upload.single('file'), async (ctx) => {
  if (!ctx.file) {
    ctx.status = 400;
    ctx.body = { error: 'Bad Request - Invalid input or missing file' };
    return;
  }

  const filePath = ctx.file.path;
  const outputFilePath = path.join('uploads', `${ctx.file.filename}.txt`);

  try {
    // Use pdftotext to extract text from PDF
    await execFilePromise('pdftotext', [filePath, outputFilePath]);

    // Read the extracted text
    const textContent = fs.readFileSync(outputFilePath, 'utf8');

    // Send the text content as response
    ctx.status = 200;
    ctx.type = 'text/plain';
    ctx.body = textContent;
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Internal Server Error - Conversion failed' };
  } finally {
    // Clean up uploaded and output files
    fs.unlinkSync(filePath);
    if (fs.existsSync(outputFilePath)) {
      fs.unlinkSync(outputFilePath);
    }
  }
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});