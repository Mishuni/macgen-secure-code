import Koa from 'koa';
import Router from 'koa-router';
import multer from '@koa/multer';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import path from 'path';
import fs from 'fs';
import util from 'util';

// Initialize Koa app and router
const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS profiles (
      username TEXT PRIMARY KEY,
      profile_page TEXT,
      profile_photo TEXT
    )
  `);
})();

// Helper function to read file
const readFile = util.promisify(fs.readFile);

// Route to add a new profile
router.post('/add_profile', upload.single('profile_photo'), async (ctx) => {
  const { username, profile_page } = ctx.request.body;
  const profilePhoto = ctx.file;

  if (!username || !profile_page || !profilePhoto) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  if (path.extname(profilePhoto.originalname).toLowerCase() !== '.png') {
    ctx.status = 400;
    ctx.body = 'Profile photo must be a PNG image';
    return;
  }

  try {
    const existingProfile = await db.get('SELECT * FROM profiles WHERE username = ?', username);
    if (existingProfile) {
      ctx.status = 403;
      ctx.body = 'Profile already exists, creation forbidden';
      return;
    }

    await db.run(
      'INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)',
      username,
      profile_page,
      profilePhoto.path
    );

    ctx.status = 201;
    ctx.body = 'Profile created successfully';
  } catch (error) {
    ctx.status = 500;
    ctx.body = 'Internal server error';
  }
});

// Route to get a user profile
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

// Route to get a user profile photo
router.get('/profile-photo/:username', async (ctx) => {
  const { username } = ctx.params;

  try {
    const profile = await db.get('SELECT profile_photo FROM profiles WHERE username = ?', username);
    if (!profile) {
      ctx.status = 404;
      ctx.body = 'Profile photo not found';
      return;
    }

    const photoPath = profile.profile_photo;
    const photo = await readFile(photoPath);

    ctx.status = 200;
    ctx.type = 'image/png';
    ctx.body = photo;
  } catch (error) {
    ctx.status = 500;
    ctx.body = 'Internal server error';
  }
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});