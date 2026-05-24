
const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });

// POST /upload - Upload an image
router.post('/upload', upload.single('file'), async (ctx) => {
  try {
    if (!ctx.file) {
      ctx.status = 400;
      ctx.body = { error: 'No file uploaded' };
      return;
    }

    const fileId = uuidv4();
    const fileExtension = path.extname(ctx.file.originalname);
    const newFileName = `${fileId}${fileExtension}`;
    const newPath = path.join(__dirname, 'uploads', newFileName);

    fs.rename(ctx.file.path, newPath, (err) => {
      if (err) {
        ctx.status = 500;
        ctx.body = { error: 'Internal server error' };
        return;
      }
    });

    ctx.status = 200;
    ctx.body = { id: fileId };
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

// GET /images/{imageId} - Share an image
router.get('/images/:imageId', async (ctx) => {
  try {
    const imageId = ctx.params.imageId;
    const files = fs.readdirSync(path.join(__dirname, 'uploads'));
    const file = files.find((f) => f.startsWith(imageId));

    if (!file) {
      ctx.status = 404;
      ctx.body = { error: 'Image not found' };
      return;
    }

    const filePath = path.join(__dirname, 'uploads', file);
    const mimeType = path.extname(file).substring(1);

    ctx.type = mimeType;
    ctx.body = fs.createReadStream(filePath);
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});