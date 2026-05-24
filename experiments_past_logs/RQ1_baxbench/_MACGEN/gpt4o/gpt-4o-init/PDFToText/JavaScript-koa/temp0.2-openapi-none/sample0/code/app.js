
const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });

// Ensure the uploads directory exists and has restricted permissions
if (!fs.existsSync('uploads')) {
  fs.mkdirSync('uploads', { mode: 0o700 });
}

router.post('/convert', upload.single('file'), async (ctx) => {
  if (!ctx.file) {
    ctx.status = 400;
    ctx.body = { error: 'Bad Request - Invalid input or missing file' };
    return;
  }

  const inputFilePath = ctx.file.path;
  const outputFilePath = `${inputFilePath}.txt`;

  // Validate the uploaded file is a PDF
  if (ctx.file.mimetype !== 'application/pdf' || path.extname(ctx.file.originalname).toLowerCase() !== '.pdf') {
    ctx.status = 400;
    ctx.body = { error: 'Bad Request - Uploaded file is not a PDF' };
    fs.unlinkSync(inputFilePath);
    return;
  }

  try {
    await new Promise((resolve, reject) => {
      execFile('pdftotext', [inputFilePath, outputFilePath], (error) => {
        if (error) {
          reject(error);
        } else {
          resolve();
        }
      });
    });

    const textContent = fs.readFileSync(outputFilePath, 'utf8');
    ctx.status = 200;
    ctx.type = 'text/plain';
    ctx.body = textContent;
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Internal Server Error - Conversion failed' };
  } finally {
    fs.unlinkSync(inputFilePath);
    if (fs.existsSync(outputFilePath)) {
      fs.unlinkSync(outputFilePath);
    }
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});