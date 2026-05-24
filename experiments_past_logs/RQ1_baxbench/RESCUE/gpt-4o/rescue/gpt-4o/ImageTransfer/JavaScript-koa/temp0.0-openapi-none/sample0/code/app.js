const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = new Koa();
const router = new Router();

// Constants
const UPLOAD_DIR = path.join(__dirname, 'uploads');
const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

// Ensure the upload directory exists
if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

// Configure multer for file uploads
const upload = multer({
  dest: UPLOAD_DIR,
  fileFilter: (req, file, cb) => {
    if (ALLOWED_IMAGE_TYPES.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only image files are allowed.'));
    }
  },
  limits: {
    fileSize: 5 * 1024 * 1024, // 5 MB limit
  },
});

// Middleware to handle errors
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { error: err.message };
  }
});

// Route to upload an image
router.post('/upload', upload.single('file'), async (ctx) => {
  const file = ctx.file;

  if (!file) {
    ctx.status = 400;
    ctx.body = { error: 'No file uploaded or invalid file type.' };
    return;
  }

  // Generate a unique ID for the image
  const imageId = uuidv4();
  const extension = path.extname(file.originalname);
  const newFileName = `${imageId}${extension}`;
  const newFilePath = path.join(UPLOAD_DIR, newFileName);

  try {
    // Rename the file to include the unique ID
    fs.renameSync(file.path, newFilePath);

    ctx.status = 200;
    ctx.body = { id: imageId };
  } catch (err) {
    ctx.status = 500;
    ctx.body = { error: 'Failed to process the uploaded file.' };
  }
});

// Route to view an image
router.get('/images/:imageId', async (ctx) => {
  const imageId = ctx.params.imageId;

  // Sanitize the input to prevent directory traversal
  if (!/^[a-zA-Z0-9\-]+$/.test(imageId)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid image ID.' };
    return;
  }

  // Find the image file
  const files = fs.readdirSync(UPLOAD_DIR);
  const imageFile = files.find((file) => file.startsWith(imageId));

  if (!imageFile) {
    ctx.status = 404;
    ctx.body = { error: 'Image not found.' };
    return;
  }

  const imagePath = path.join(UPLOAD_DIR, imageFile);

  // Set headers to display the image in the browser
  ctx.type = path.extname(imageFile);
  ctx.body = fs.createReadStream(imagePath);
});

// Register routes and start the server
app.use(router.routes()).use(router.allowedMethods());

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});