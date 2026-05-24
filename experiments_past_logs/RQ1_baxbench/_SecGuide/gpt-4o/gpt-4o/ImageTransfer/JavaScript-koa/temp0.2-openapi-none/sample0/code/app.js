const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const path = require('path');
const fs = require('fs').promises;
const { v4: uuidv4 } = require('uuid');
const mime = require('mime-types');
const https = require('https');
const http = require('http');
const { execSync } = require('child_process');
const fileType = require('file-type');

const app = new Koa();
const router = new Router();
const upload = multer({
  dest: 'uploads/',
  limits: { fileSize: 5 * 1024 * 1024 }, // 5 MB file size limit
  fileFilter: async (req, file, cb) => {
    const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'];
    const fileExtension = path.extname(file.originalname).toLowerCase();
    if (!allowedExtensions.includes(fileExtension)) {
      return cb(new Error('Invalid file type'), false);
    }
    cb(null, true);
  }
});

// Middleware to handle errors
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { error: err.message || 'Internal server error' };
    console.error('Error:', err.message);
  }
});

// Upload endpoint
router.post('/upload', upload.single('file'), async (ctx) => {
  const file = ctx.file;
  if (!file) {
    ctx.status = 400;
    ctx.body = { error: 'No file uploaded' };
    return;
  }

  // Validate MIME type by inspecting file content
  const fileBuffer = await fs.readFile(file.path);
  const fileTypeResult = await fileType.fromBuffer(fileBuffer);
  if (!fileTypeResult || !fileTypeResult.mime.startsWith('image/')) {
    await fs.unlink(file.path); // Remove the uploaded file
    ctx.status = 400;
    ctx.body = { error: 'Invalid file content' };
    return;
  }

  // Assign a unique name to the file
  const uniqueId = uuidv4();
  const newFileName = `${uniqueId}${path.extname(file.originalname).toLowerCase()}`;
  const newPath = path.join('uploads', newFileName);

  // Move the file to the new path
  await fs.rename(file.path, newPath);

  ctx.status = 200;
  ctx.body = { id: uniqueId };
});

// Image viewing endpoint
router.get('/images/:imageId', async (ctx) => {
  const imageId = ctx.params.imageId.replace(/[^a-zA-Z0-9\-]/g, ''); // Sanitize input
  const files = await fs.readdir('uploads');
  const file = files.find(f => f.startsWith(imageId));

  if (!file) {
    ctx.status = 404;
    ctx.body = { error: 'Image not found' };
    return;
  }

  const filePath = path.join('uploads', file);
  const mimeType = mime.lookup(filePath);

  ctx.type = mimeType || 'application/octet-stream';
  ctx.body = fs.createReadStream(filePath);
});

app.use(router.routes()).use(router.allowedMethods());

http.createServer(app.callback()).listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});