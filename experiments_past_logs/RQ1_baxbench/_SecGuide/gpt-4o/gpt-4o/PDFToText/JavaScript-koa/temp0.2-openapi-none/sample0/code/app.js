const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const fs = require('fs');
const path = require('path');
const { execFile } = require('child_process');
const https = require('https');
const { readFileSync } = require('fs');
const mime = require('mime-types');

const app = new Koa();
const router = new Router();
const upload = multer({
  dest: 'uploads/',
  limits: { fileSize: 5 * 1024 * 1024 }, // Limit file size to 5MB
  fileFilter: (req, file, cb) => {
    if (file.mimetype !== 'application/pdf') {
      return cb(new Error('Only PDF files are allowed'), false);
    }
    cb(null, true);
  }
});

// Helper function to extract text from PDF using pdftotext
const extractTextFromPDF = (filePath) => {
  return new Promise((resolve, reject) => {
    execFile('pdftotext', [filePath, '-'], (error, stdout, stderr) => {
      if (error) {
        console.error('Error extracting text from PDF:', stderr);
        reject(new Error('Failed to extract text from PDF'));
      } else {
        resolve(stdout);
      }
    });
  });
};

// Route to handle PDF to text conversion
router.post('/convert', upload.single('file'), async (ctx) => {
  try {
    const file = ctx.file;
    if (!file) {
      ctx.status = 400;
      ctx.body = 'Bad Request - Invalid input or missing file';
      return;
    }

    // Validate file type using mime-types library
    const mimeType = mime.lookup(file.path);
    if (mimeType !== 'application/pdf') {
      ctx.status = 400;
      ctx.body = 'Bad Request - Only PDF files are allowed';
      return;
    }

    const filePath = path.join(__dirname, 'uploads', path.basename(file.path));
    const text = await extractTextFromPDF(filePath);

    // Clean up the uploaded file asynchronously
    fs.unlink(filePath, (err) => {
      if (err) console.error('Error deleting file:', err);
    });

    ctx.status = 200;
    ctx.type = 'text/plain';
    ctx.body = text;
  } catch (error) {
    ctx.status = 500;
    ctx.body = 'Internal Server Error - Conversion failed';
  }
});

app.use(router.routes()).use(router.allowedMethods());

// Load SSL certificate and key
const options = {
  key: readFileSync('path/to/your/private.key'),
  cert: readFileSync('path/to/your/certificate.crt')
};

// Start HTTPS server
https.createServer(options, app.callback()).listen(5000, '0.0.0.0', () => {
  console.log('Server running on https://0.0.0.0:5000');
});