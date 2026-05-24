import fastify from 'fastify';
import multipart from '@fastify/multipart';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import path from 'path';
import fs from 'fs';

// Initialize Fastify app
const app = fastify();
const PORT = 5000;

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
      profile_photo BLOB
    )
  `);
})();

// Register multipart plugin
app.register(multipart);

// Route to add a new profile
app.post('/add_profile', async (req, reply) => {
  const parts = req.parts();
  let username, profilePage, profilePhoto;

  for await (const part of parts) {
    if (part.fieldname === 'username') {
      username = part.value;
    } else if (part.fieldname === 'profile_page') {
      profilePage = part.value;
    } else if (part.fieldname === 'profile_photo') {
      profilePhoto = await part.toBuffer();
    }
  }

  // Input validation
  if (!username || !/^[a-zA-Z0-9]+$/.test(username) || username.length > 50) {
    return reply.status(400).send('Invalid username');
  }
  if (!profilePage || typeof profilePage !== 'string') {
    return reply.status(400).send('Invalid profile page');
  }
  if (!profilePhoto || !Buffer.isBuffer(profilePhoto)) {
    return reply.status(400).send('Invalid profile photo');
  }

  try {
    await db.run(
      'INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)',
      [username, profilePage, profilePhoto]
    );
    reply.status(201).send('Profile created successfully');
  } catch (err) {
    if (err.code === 'SQLITE_CONSTRAINT') {
      reply.status(403).send('Profile already exists, creation forbidden');
    } else {
      reply.status(500).send('Internal server error');
    }
  }
});

// Route to get user profile
app.get('/profile/:username', async (req, reply) => {
  const { username } = req.params;
  const profile = await db.get('SELECT profile_page FROM profiles WHERE username = ?', [username]);

  if (profile) {
    reply.type('text/html').send(profile.profile_page);
  } else {
    reply.status(404).send('Profile not found');
  }
});

// Route to get user profile photo
app.get('/profile-photo/:username', async (req, reply) => {
  const { username } = req.params;
  const profile = await db.get('SELECT profile_photo FROM profiles WHERE username = ?', [username]);

  if (profile) {
    reply.type('image/png').send(profile.profile_photo);
  } else {
    reply.status(404).send('Profile photo not found');
  }
});

// Start the server
app.listen({ port: PORT, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});