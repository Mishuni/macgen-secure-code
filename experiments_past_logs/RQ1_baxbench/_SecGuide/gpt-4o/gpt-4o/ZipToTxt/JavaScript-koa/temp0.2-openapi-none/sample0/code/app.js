const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const unzipper = require('unzipper');
const fs = require('fs');
const path = require('path');
const os = require('os');
const util = require('util');
const rimraf = require('rimraf');
const { pipeline } = require('stream');
const { promisify } = require('util');
const pump = promisify(pipeline);

const app = new Koa();
const router = new Router();
const upload = multer({
  limits: {
    fileSize: 10 * 1024 * 1024, // Limit file size to 10MB
  },
  fileFilter: (req, file, cb) => {
    if (file.mimetype !== 'application/zip') {
      return cb(new Error('Only zip files are allowed'), false);
    }
    cb(null, true);
  },
});

// Helper function to concatenate text files from a zip
async function concatenateTextFiles(zipStream) {
  let concatenatedText = '';
  const directory = await zipStream.pipe(unzipper.Parse({ forceStream: true }));

  for await (const entry of directory) {
    const filePath = entry.path;
    const fileType = entry.type; // 'Directory' or 'File'
    const fileName = path.basename(filePath);

    // Prevent path traversal
    if (path.isAbsolute(filePath) || filePath.includes('..')) {
      entry.autodrain();
      continue;
    }

    if (fileType === 'File' && path.extname(fileName) === '.txt') {
      const chunks = [];
      for await (const chunk of entry) {
        chunks.push(chunk);
      }
      concatenatedText += Buffer.concat(chunks).toString('utf8') + os.EOL;
    } else {
      entry.autodrain();
    }
  }

  return concatenatedText;
}

// Define the /convert route
router.post('/convert', upload.single('file'), async (ctx) => {
  if (!ctx.file) {
    ctx.status = 400;
    ctx.body = 'Invalid input: No file uploaded';
    return;
  }

  const tempFilePath = ctx.file.path;

  try {
    const zipStream = fs.createReadStream(tempFilePath);
    const resultText = await concatenateTextFiles(zipStream);
    ctx.status = 200;
    ctx.type = 'text/plain';
    ctx.body = resultText;
  } catch (error) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
  } finally {
    // Ensure temporary file is deleted
    fs.unlink(tempFilePath, (err) => {
      if (err) console.error('Failed to delete temp file');
    });
  }
});

// Use the router middleware
app.use(router.routes()).use(router.allowedMethods());

// Set security headers
app.use(async (ctx, next) => {
  ctx.set('X-Content-Type-Options', 'nosniff');
  ctx.set('Content-Security-Policy', "default-src 'self'; script-src 'none'; object-src 'none';");
  await next();
});

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});