const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const fs = require('fs');
const { execFile } = require('child_process');
const path = require('path');

const app = new Koa();
const router = new Router();
const upload = multer({
  dest: 'uploads/',
  limits: { fileSize: 5 * 1024 * 1024 }, // 5 MB limit
  fileFilter: (req, file, cb) => {
    if (file.mimetype !== 'application/pdf') {
      return cb(new Error('Only PDF files are allowed'), false);
    }
    cb(null, true);
  }
});

router.post('/concatenate', upload.array('files'), async (ctx) => {
  try {
    const files = ctx.files;
    if (!files || files.length === 0) {
      ctx.status = 400;
      ctx.body = { error: "Invalid input or missing files." };
      return;
    }

    const inputFiles = files.map(file => path.resolve('uploads', path.basename(file.path)));
    const outputFilePath = path.resolve('uploads', `concatenated-${Date.now()}.pdf`);

    await new Promise((resolve, reject) => {
      execFile('pdfunite', [...inputFiles, outputFilePath], (error) => {
        if (error) {
          reject(error);
        } else {
          resolve();
        }
      });
    });

    ctx.set('Content-Type', 'application/pdf');
    ctx.body = fs.createReadStream(outputFilePath);

    // Clean up temporary files
    ctx.res.on('finish', () => {
      inputFiles.forEach(file => fs.unlink(file, () => {}));
      fs.unlink(outputFilePath, () => {});
    });

  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: "An error occurred while processing the files." };
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});