const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const util = require('util');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });
const execPromise = util.promisify(exec);

router.post('/concatenate', upload.array('files'), async (ctx) => {
  try {
    const files = ctx.files;
    if (!files || files.length === 0) {
      ctx.status = 400;
      ctx.body = { error: 'Invalid input or missing files.' };
      return;
    }

    // Validate file types
    for (const file of files) {
      if (path.extname(file.originalname).toLowerCase() !== '.pdf') {
        ctx.status = 400;
        ctx.body = { error: 'All files must be PDFs.' };
        return;
      }
    }

    // Generate a unique output file path
    const outputFilePath = path.join('uploads', `concatenated_${Date.now()}.pdf`);

    // Construct the command for pdfunite
    const filePaths = files.map(file => file.path);
    const command = `pdfunite ${filePaths.join(' ')} ${outputFilePath}`;

    // Execute the command
    await execPromise(command);

    // Send the concatenated PDF as response
    ctx.set('Content-Type', 'application/pdf');
    ctx.body = fs.createReadStream(outputFilePath);

    // Clean up temporary files after response is sent
    ctx.res.on('finish', () => {
      files.forEach(file => fs.unlink(file.path, () => {}));
      fs.unlink(outputFilePath, () => {});
    });

  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'An error occurred while processing the files.' };
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});