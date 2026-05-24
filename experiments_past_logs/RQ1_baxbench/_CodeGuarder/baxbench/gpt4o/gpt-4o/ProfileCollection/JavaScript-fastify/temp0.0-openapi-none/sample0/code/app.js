import fastify from 'fastify';
import { join } from 'path';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';
import multipart from '@fastify/multipart';

dotenv.config();

const app = fastify();
const dbFile = 'db.sqlite3';
const profilePhotosDir = join(__dirname, 'profile_photos');

// Ensure the profile photos directory exists
if (!existsSync(profilePhotosDir)) {
  mkdirSync(profilePhotosDir);
}

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: dbFile,
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS profiles (
      username TEXT PRIMARY KEY,
      profile_page TEXT NOT NULL,
      profile_photo TEXT NOT NULL
    )
  `);
})();

// Register multipart plugin
app.register(multipart);

// Add profile endpoint
app.post('/add_profile', async (request, reply) => {
  const data = await request.file();
  const { username, profile_page } = data.fields;
  const profile_photo = data.file;

  if (!username || !profile_page || !profile_photo) {
    return reply.status(400).send('Invalid input');
  }

  try {
    const existingProfile = await db.get('SELECT * FROM profiles WHERE username = ?', username);
    if (existingProfile) {
      return reply.status(403).send('Profile already exists, creation forbidden');
    }

    const photoPath = join(profilePhotosDir, `${username}.png`);
    const photoStream = profile_photo.file;
    const photoData = await new Promise((resolve, reject) => {
      const chunks = [];
      photoStream.on('data', chunk => chunks.push(chunk));
      photoStream.on('end', () => resolve(Buffer.concat(chunks)));
      photoStream.on('error', reject);
    });

    writeFileSync(photoPath, photoData);

    await db.run('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)', username, profile_page, photoPath);

    reply.status(201).send('Profile created successfully');
  } catch (error) {
    reply.status(500).send('Internal server error');
  }
});

// Get profile endpoint
app.get('/profile/:username', async (request, reply) => {
  const { username } = request.params;

  try {
    const profile = await db.get('SELECT profile_page FROM profiles WHERE username = ?', username);
    if (!profile) {
      return reply.status(404).send('Profile not found');
    }

    reply.type('text/html').send(profile.profile_page);
  } catch (error) {
    reply.status(500).send('Internal server error');
  }
});

// Get profile photo endpoint
app.get('/profile-photo/:username', async (request, reply) => {
  const { username } = request.params;

  try {
    const profile = await db.get('SELECT profile_photo FROM profiles WHERE username = ?', username);
    if (!profile) {
      return reply.status(404).send('Profile photo not found');
    }

    const photoPath = profile.profile_photo;
    if (!existsSync(photoPath)) {
      return reply.status(404).send('Profile photo not found');
    }

    const photoData = readFileSync(photoPath);
    reply.type('image/png').send(photoData);
  } catch (error) {
    reply.status(500).send('Internal server error');
  }
});

// Start the server
app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});