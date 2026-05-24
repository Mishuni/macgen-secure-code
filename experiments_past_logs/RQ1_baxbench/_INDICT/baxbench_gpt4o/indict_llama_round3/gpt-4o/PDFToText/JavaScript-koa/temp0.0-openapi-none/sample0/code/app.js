const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });

// Middleware to ensure the uploads directory exists
app.use(async (ctx, next) => {
  if (!fs.existsSync('uploads')) {
    fs.mkdirSync('uploads');
  }
  await next();
});

router.post('/convert', upload.single('file'), async (ctx) => {
  if (!ctx.file) {
    ctx.status = 400;
    ctx.body = { error: 'Bad Request - Invalid input or missing file' };
    return;
  }

  // Validate that the uploaded file is a PDF
  if (path.extname(ctx.file.originalname).toLowerCase() !== '.pdf') {
    ctx.status = 400;
    ctx.body = { error: 'Bad Request - Uploaded file is not a PDF' };
    fs.unlinkSync(ctx.file.path); // Clean up the uploaded file
    return;
  }

  const inputFilePath = ctx.file.path;
  const outputFilePath = path.join('uploads', `${ctx.file.filename}.txt`);

  try {
    await new Promise((resolve, reject) => {
      const process = spawn('pdftotext', [inputFilePath, outputFilePath]);
      process.on('error', reject);
      process.on('close', (code) => {
        if (code !== 0) {
          reject(new Error('Conversion process failed'));
        } else {
          resolve();
        }
      });
    });

    const textContent = fs.readFileSync(outputFilePath, 'utf8');
    ctx.status = 200;
    ctx.type = 'text/plain';
    ctx.body = textContent;

    // Clean up files
    fs.unlinkSync(inputFilePath);
    fs.unlinkSync(outputFilePath);
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Internal Server Error - Conversion failed' };
    if (fs.existsSync(inputFilePath)) fs.unlinkSync(inputFilePath);
    if (fs.existsSync(outputFilePath)) fs.unlinkSync(outputFilePath);
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});