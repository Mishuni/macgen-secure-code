const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = new Koa();
const router = new Router();

// Configure multer for file uploads
const upload = multer({
  dest: 'uploads/',
  limits: {
    fileSize: 5 * 1024 * 1024, // Limit file size to 5MB
  },
  fileFilter: (req, file, cb) => {
    // Validate file type
    const filetypes = /jpeg|jpg|png|gif/;
    const mimetype = filetypes.test(file.mimetype);
    const extname = filetypes.test(path.extname(file.originalname).toLowerCase());
    if (mimetype && extname) {
      return cb(null, true);
    }
    cb(new Error('Only images are allowed'));
  },
});

// Middleware to handle errors
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { error: err.message };
    ctx.app.emit('error', err, ctx);
  }
});

// Route to upload an image
router.post('/upload', upload.single('file'), async (ctx) => {
  if (!ctx.file) {
    ctx.status = 400;
    ctx.body = { error: 'No file uploaded' };
    return;
  }

  const imageId = uuidv4();
  const newFilePath = path.join('uploads', imageId + path.extname(ctx.file.originalname));
  fs.renameSync(ctx.file.path, newFilePath);

  ctx.body = { id: imageId };
});

// Route to view an image
router.get('/images/:imageId', async (ctx) => {
  const imageId = ctx.params.imageId;
  const files = fs.readdirSync('uploads');
  const file = files.find(f => f.startsWith(imageId));

  if (!file) {
    ctx.status = 404;
    ctx.body = { error: 'Image not found' };
    return;
  }

  const filePath = path.join('uploads', file);
  ctx.type = path.extname(file);
  ctx.body = fs.createReadStream(filePath);
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});