const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const multer = require('@koa/multer');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const path = require('path');
const fs = require('fs').promises;
const dotenv = require('dotenv');
const mime = require('mime-types');
const helmet = require('koa-helmet');
const DOMPurify = require('dompurify');
const { JSDOM } = require('jsdom');

dotenv.config();

const app = new Koa();
const router = new Router();
const upload = multer({
  dest: 'uploads/',
  limits: { fileSize: 2 * 1024 * 1024 }, // Limit file size to 2MB
  fileFilter: (req, file, cb) => {
    const allowedMimeTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (allowedMimeTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type'));
    }
  }
});

const DB_PATH = process.env.DB_PATH || 'db.sqlite3';

// Initialize SQLite database
let db;
async function initDb() {
  if (!db) {
    db = await open({
      filename: DB_PATH,
      driver: sqlite3.Database
    });

    await db.exec(`
      CREATE TABLE IF NOT EXISTS profiles (
        username TEXT PRIMARY KEY,
        profile_page TEXT,
        profile_photo_path TEXT
      )
    `);
  }
  return db;
}

// Middleware to handle errors
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = 'An error occurred';
    console.error(err);
  }
});

// Use helmet for basic security hardening
app.use(helmet());

// Add profile route
router.post('/add_profile', upload.single('profile_photo'), async (ctx) => {
  const { username, profile_page } = ctx.request.body;
  const profile_photo = ctx.file;

  if (!username || !profile_page || !profile_photo) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  const db = await initDb();

  try {
    const existingProfile = await db.get('SELECT * FROM profiles WHERE username = ?', username);
    if (existingProfile) {
      ctx.status = 403;
      ctx.body = 'Profile already exists, creation forbidden';
      return;
    }

    const window = new JSDOM('').window;
    const DOMPurifyInstance = DOMPurify(window);
    const sanitizedProfilePage = DOMPurifyInstance.sanitize(profile_page);

    const uniqueFilename = `${Date.now()}-${Math.random().toString(36).substring(2, 15)}-${path.basename(profile_photo.originalname)}`;
    const profilePhotoPath = path.join(__dirname, 'uploads', uniqueFilename);

    await fs.rename(profile_photo.path, profilePhotoPath);

    await db.run('INSERT INTO profiles (username, profile_page, profile_photo_path) VALUES (?, ?, ?)', username, sanitizedProfilePage, profilePhotoPath);

    ctx.status = 201;
    ctx.body = 'Profile created successfully';
  } catch (err) {
    console.error(err);
    ctx.status = 500;
    ctx.body = 'Internal server error';
  }
});

// Get profile route
router.get('/profile/:username', async (ctx) => {
  const { username } = ctx.params;
  const db = await initDb();

  try {
    const profile = await db.get('SELECT profile_page FROM profiles WHERE username = ?', username);
    if (!profile) {
      ctx.status = 404;
      ctx.body = 'Profile not found';
      return;
    }

    ctx.status = 200;
    ctx.type = 'text/html';
    ctx.body = profile.profile_page;
  } catch (err) {
    console.error(err);
    ctx.status = 500;
    ctx.body = 'Internal server error';
  }
});

// Get profile photo route
router.get('/profile-photo/:username', async (ctx) => {
  const { username } = ctx.params;
  const db = await initDb();

  try {
    const profile = await db.get('SELECT profile_photo_path FROM profiles WHERE username = ?', username);
    if (!profile) {
      ctx.status = 404;
      ctx.body = 'Profile photo not found';
      return;
    }

    const mimeType = mime.lookup(profile.profile_photo_path);
    if (!mimeType) {
      ctx.status = 400;
      ctx.body = 'Invalid file type';
      return;
    }

    ctx.status = 200;
    ctx.type = mimeType;
    ctx.body = fs.createReadStream(profile.profile_photo_path);
  } catch (err) {
    console.error(err);
    ctx.status = 500;
    ctx.body = 'Internal server error';
  }
});

app
  .use(bodyParser())
  .use(router.routes())
  .use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});