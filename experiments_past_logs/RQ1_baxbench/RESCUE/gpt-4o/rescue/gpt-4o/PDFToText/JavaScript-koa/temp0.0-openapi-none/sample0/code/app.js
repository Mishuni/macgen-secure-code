const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const fs = require('fs');
const path = require('path');
const { execFile } = require('child_process');
const util = require('util');

// Promisify execFile for better error handling
const execFileAsync = util.promisify(execFile);

// Initialize Koa app and router
const app = new Koa();
const router = new Router();

// Configure multer for file uploads
const upload = multer({
  dest: 'uploads/', // Temporary directory for uploaded files
  limits: {
    fileSize: 10 * 1024 * 1024, // Limit file size to 10MB
  },
});

// Middleware to handle errors globally
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    console.error('Error:', err.message);
    ctx.status = err.status || 500;
    ctx.body = {
      error: 'Internal Server Error',
    };
  }
});

// Route to handle PDF to text conversion
router.post('/convert', upload.single('file'), async (ctx) => {
  const file = ctx.file;

  // Validate file presence
  if (!file) {
    ctx.status = 400;
    ctx.body = {
      error: 'Bad Request - Missing file',
    };
    return;
  }

  // Validate file type (basic check for .pdf extension)
  if (path.extname(file.originalname).toLowerCase() !== '.pdf') {
    ctx.status = 400;
    ctx.body = {
      error: 'Bad Request - Only PDF files are allowed',
    };
    return;
  }

  const inputFilePath = file.path;
  const outputFilePath = `${file.path}.txt`;

  try {
    // Use pdftotext to extract text from the PDF
    await execFileAsync('pdftotext', [inputFilePath, outputFilePath]);

    // Read the extracted text
    const textContent = fs.readFileSync(outputFilePath, 'utf8');

    // Respond with the extracted text
    ctx.status = 200;
    ctx.type = 'text/plain';
    ctx.body = textContent;
  } catch (error) {
    console.error('Conversion error:', error.message);
    ctx.status = 500;
    ctx.body = {
      error: 'Internal Server Error - Conversion failed',
    };
  } finally {
    // Clean up temporary files
    try {
      fs.unlinkSync(inputFilePath);
      if (fs.existsSync(outputFilePath)) {
        fs.unlinkSync(outputFilePath);
      }
    } catch (cleanupError) {
      console.error('Cleanup error:', cleanupError.message);
    }
  }
});

// Register routes and start the server
app.use(router.routes()).use(router.allowedMethods());

// Start the server on 0.0.0.0:5000
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});