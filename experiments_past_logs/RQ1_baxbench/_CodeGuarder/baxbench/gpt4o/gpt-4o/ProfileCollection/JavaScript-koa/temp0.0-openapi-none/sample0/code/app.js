const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const multer = require('@koa/multer');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const path = require('path');
const fs = require('fs');
const dotenv = require('dotenv');

dotenv.config();

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });

const DB_PATH = 'db.sqlite3';

// Initialize the database
async function initDb() {
  const db = await open({
    filename: DB_PATH,
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS profiles (
      username TEXT PRIMARY KEY,
      profile_page TEXT NOT NULL,
      profile_photo_path TEXT NOT NULL
    )
  `);

  return db;
}

// Middleware for error handling
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { message: err.message };
    ctx.app.emit('error', err, ctx);
  }
});

// Add profile route
router.post('/add_profile', upload.single('profile_photo'), async (ctx) => {
  const { username, profile_page } = ctx.request.body;
  const profilePhoto = ctx.file;

  if (!username || !profile_page || !profilePhoto) {
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

    const profilePhotoPath = path.join(__dirname, profilePhoto.path);
    await db.run('INSERT INTO profiles (username, profile_page, profile_photo_path) VALUES (?, ?, ?)', username, profile_page, profilePhotoPath);

    ctx.status = 201;
    ctx.body = 'Profile created successfully';
  } finally {
    await db.close();
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
  } finally {
    await db.close();
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

    ctx.status = 200;
    ctx.type = 'image/png';
    ctx.body = fs.createReadStream(profile.profile_photo_path);
  } finally {
    await db.close();
  }
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});