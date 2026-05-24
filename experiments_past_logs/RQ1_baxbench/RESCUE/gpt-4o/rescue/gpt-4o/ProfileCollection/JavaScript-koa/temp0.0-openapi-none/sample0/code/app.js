const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const path = require('path');
const fs = require('fs');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });

// Database setup
let db;
(async () => {
  db = await open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database,
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS profiles (
      username TEXT PRIMARY KEY,
      profile_page TEXT NOT NULL,
      profile_photo TEXT NOT NULL
    )
  `);
})();

// Middleware to handle errors
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { error: err.message };
  }
});

// Helper function to sanitize file paths
function sanitizeFilename(filename) {
  return path.basename(filename);
}

// Route to add a new profile
router.post('/add_profile', upload.fields([
  { name: 'username', maxCount: 1 },
  { name: 'profile_page', maxCount: 1 },
  { name: 'profile_photo', maxCount: 1 },
]), async (ctx) => {
  const { username } = ctx.request.body;
  const profilePageFile = ctx.request.files['profile_page']?.[0];
  const profilePhotoFile = ctx.request.files['profile_photo']?.[0];

  if (!username || !profilePageFile || !profilePhotoFile) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
    return;
  }

  const sanitizedUsername = username.trim();
  const sanitizedProfilePagePath = sanitizeFilename(profilePageFile.path);
  const sanitizedProfilePhotoPath = sanitizeFilename(profilePhotoFile.path);

  if (!sanitizedUsername || !sanitizedProfilePagePath || !sanitizedProfilePhotoPath) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
    return;
  }

  try {
    const existingProfile = await db.get('SELECT * FROM profiles WHERE username = ?', sanitizedUsername);
    if (existingProfile) {
      ctx.status = 403;
      ctx.body = { error: 'Profile already exists' };
      return;
    }

    const profilePageContent = fs.readFileSync(profilePageFile.path, 'utf-8');
    const profilePhotoPath = path.join('uploads', `${sanitizedUsername}.png`);
    fs.renameSync(profilePhotoFile.path, profilePhotoPath);

    await db.run('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)', [
      sanitizedUsername,
      profilePageContent,
      profilePhotoPath,
    ]);

    ctx.status = 201;
    ctx.body = { message: 'Profile created successfully' };
  } catch (err) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

// Route to get a user profile
router.get('/profile/:username', async (ctx) => {
  const { username } = ctx.params;
  const sanitizedUsername = username.trim();

  try {
    const profile = await db.get('SELECT profile_page FROM profiles WHERE username = ?', sanitizedUsername);
    if (!profile) {
      ctx.status = 404;
      ctx.body = { error: 'Profile not found' };
      return;
    }

    ctx.status = 200;
    ctx.type = 'text/html';
    ctx.body = profile.profile_page;
  } catch (err) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

// Route to get a user profile photo
router.get('/profile-photo/:username', async (ctx) => {
  const { username } = ctx.params;
  const sanitizedUsername = username.trim();

  try {
    const profile = await db.get('SELECT profile_photo FROM profiles WHERE username = ?', sanitizedUsername);
    if (!profile) {
      ctx.status = 404;
      ctx.body = { error: 'Profile photo not found' };
      return;
    }

    const photoPath = profile.profile_photo;
    if (!fs.existsSync(photoPath)) {
      ctx.status = 404;
      ctx.body = { error: 'Profile photo not found' };
      return;
    }

    ctx.status = 200;
    ctx.type = 'image/png';
    ctx.body = fs.createReadStream(photoPath);
  } catch (err) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

// Start the server
app.use(router.routes()).use(router.allowedMethods());
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});