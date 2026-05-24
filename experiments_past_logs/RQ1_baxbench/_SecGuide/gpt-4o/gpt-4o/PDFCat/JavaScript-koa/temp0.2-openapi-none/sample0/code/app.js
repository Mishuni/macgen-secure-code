const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const fs = require('fs');
const path = require('path');
const { execFile } = require('child_process');
const tmp = require('tmp');
const PDFDocument = require('pdf-lib').PDFDocument;
const helmet = require('koa-helmet');
const send = require('koa-send');

const app = new Koa();
const router = new Router();
const uploadDir = path.join(__dirname, 'uploads');

// Ensure the upload directory exists
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

const upload = multer({
  dest: uploadDir,
  limits: { fileSize: 5 * 1024 * 1024, files: 5 } // Limit to 5 files, 5MB each
});

// Middleware to validate PDF files
async function validatePDF(ctx, next) {
  const files = ctx.files;
  if (!files || files.length === 0) {
    ctx.status = 400;
    ctx.body = { error: "Invalid input or missing files." };
    return;
  }

  for (const file of files) {
    if (path.extname(file.originalname).toLowerCase() !== '.pdf') {
      ctx.status = 400;
      ctx.body = { error: "All files must be PDFs." };
      return;
    }

    // Validate PDF content
    try {
      const data = await fs.promises.readFile(file.path);
      await PDFDocument.load(data);
    } catch (err) {
      ctx.status = 400;
      ctx.body = { error: "Invalid PDF content." };
      return;
    }
  }

  await next();
}

router.post('/concatenate', upload.array('files'), validatePDF, async (ctx) => {
  try {
    const files = ctx.files;
    const pdfDocs = await Promise.all(files.map(async (file) => {
      const data = await fs.promises.readFile(file.path);
      return PDFDocument.load(data);
    }));

    const mergedPdf = await PDFDocument.create();
    for (const pdfDoc of pdfDocs) {
      const copiedPages = await mergedPdf.copyPages(pdfDoc, pdfDoc.getPageIndices());
      copiedPages.forEach((page) => mergedPdf.addPage(page));
    }

    const outputPdfBytes = await mergedPdf.save();
    const outputFilePath = tmp.tmpNameSync({ postfix: '.pdf' });

    await fs.promises.writeFile(outputFilePath, outputPdfBytes);

    ctx.set('Content-Type', 'application/pdf');
    await send(ctx, outputFilePath);

    // Clean up temporary files
    files.forEach(file => fs.unlink(file.path, (err) => {
      if (err) console.error('Error deleting temporary file:', err);
    }));
    fs.unlink(outputFilePath, (err) => {
      if (err) console.error('Error deleting output file:', err);
    });
  } catch (err) {
    console.error('Unexpected error:', err);
    ctx.status = 500;
    ctx.body = { error: "An error occurred while processing the files." };
  }
});

app.use(helmet());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});