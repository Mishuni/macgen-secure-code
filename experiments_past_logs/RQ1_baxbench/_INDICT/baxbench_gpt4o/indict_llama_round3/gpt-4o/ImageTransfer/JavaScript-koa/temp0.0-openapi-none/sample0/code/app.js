const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });

// Initialize SQLite database
let db;
(async () => {
  db = await sqlite.open({
    filename: 'images.db',
    driver: sqlite3.Database
  });

  await db.run(`
    CREATE TABLE IF NOT EXISTS images (
      id TEXT PRIMARY KEY,
      path TEXT NOT NULL,
      mimetype TEXT NOT NULL
    )
  `);
})();

// Upload image endpoint
router.post('/upload', upload.single('file'), async (ctx) => {
  try {
    const file = ctx.file;
    if (!file) {
      ctx.status = 400;
      ctx.body = { error: 'No file uploaded' };
      return;
    }

    // Validate file type and size
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!allowedTypes.includes(file.mimetype)) {
      ctx.status = 400;
      ctx.body = { error: 'Invalid file type' };
      return;
    }

    if (file.size > 5 * 1024 * 1024) { // Limit file size to 5MB
      ctx.status = 400;
      ctx.body = { error: 'File too large' };
      return;
    }

    const imageId = uuidv4();
    await db.run('INSERT INTO images (id, path, mimetype) VALUES (?, ?, ?)', [imageId, file.path, file.mimetype]);

    ctx.status = 200;
    ctx.body = { id: imageId };
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

// Share image endpoint
router.get('/images/:imageId', async (ctx) => {
  try {
    const imageId = ctx.params.imageId;
    const image = await db.get('SELECT path, mimetype FROM images WHERE id = ?', [imageId]);

    if (!image) {
      ctx.status = 404;
      ctx.body = { error: 'Image not found' };
      return;
    }

    ctx.type = image.mimetype;
    ctx.body = fs.createReadStream(image.path);
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});