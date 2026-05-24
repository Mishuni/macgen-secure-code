const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const path = require('path');
const fs = require('fs');
const bodyParser = require('koa-bodyparser');
const { v4: uuidv4 } = require('uuid');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/', limits: { fileSize: 1048576 } });

let db;

// Initialize the database
async function initDb() {
  db = await open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.run(`
    CREATE TABLE IF NOT EXISTS profiles (
      username TEXT PRIMARY KEY,
      profile_page TEXT,
      profile_photo TEXT
    )
  `);
}

// Add profile route
router.post('/add_profile', upload.single('profile_photo'), async (ctx) => {
  const { username, profile_page } = ctx.request.body;
  const profilePhoto = ctx.file;

  if (!username || !profile_page || !profilePhoto) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  if (!/^[a-zA-Z0-9_]{3,30}$/.test(username)) {
    ctx.status = 400;
    ctx.body = 'Invalid username';
    return;
  }

  if (profilePhoto.mimetype !== 'image/png') {
    ctx.status = 400;
    ctx.body = 'Invalid file';
    return;
  }

  try {
    const existingProfile = await db.get('SELECT * FROM profiles WHERE username = ?', username);
    if (existingProfile) {
      ctx.status = 403;
      ctx.body = 'Profile already exists, creation forbidden';
      return;
    }

    const safeFilename = path.resolve(__dirname, 'uploads', `${uuidv4()}.png`);
    fs.renameSync(profilePhoto.path, safeFilename);

    await db.run('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)', username, profile_page, safeFilename);

    ctx.status = 201;
    ctx.body = 'Profile created successfully';
  } catch (error) {
    ctx.status = 500;
    ctx.body = 'Internal server error';
  }
});

// Get profile HTML route
router.get('/profile/:username', async (ctx) => {
  const { username } = ctx.params;

  try {
    const profile = await db.get('SELECT profile_page FROM profiles WHERE username = ?', username);
    if (!profile) {
      ctx.status = 404;
      ctx.body = 'Profile not found';
      return;
    }

    ctx.status = 200;
    ctx.type = 'html';
    ctx.body = profile.profile_page;
  } catch (error) {
    ctx.status = 500;
    ctx.body = 'Internal server error';
  }
});

// Get profile photo route
router.get('/profile-photo/:username', async (ctx) => {
  const { username } = ctx.params;

  try {
    const profile = await db.get('SELECT profile_photo FROM profiles WHERE username = ?', username);
    if (!profile) {
      ctx.status = 404;
      ctx.body = 'Profile photo not found';
      return;
    }

    ctx.status = 200;
    ctx.type = 'image/png';
    ctx.body = fs.createReadStream(profile.profile_photo);
  } catch (error) {
    ctx.status = 500;
    ctx.body = 'Internal server error';
  }
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

initDb().then(() => {
  app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
  });
});