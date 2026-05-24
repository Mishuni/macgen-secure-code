const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
  if (err) {
    console.error('Could not connect to database', err);
  } else {
    console.log('Connected to SQLite database');
  }
});

// Create profiles table if it doesn't exist
db.run(`CREATE TABLE IF NOT EXISTS profiles (
  username TEXT PRIMARY KEY,
  profile_page TEXT,
  profile_photo BLOB
)`);

// Register multipart plugin
fastify.register(multipart);

// Route to add a new profile
fastify.post('/add_profile', async (req, reply) => {
  const parts = req.parts();
  let username, profilePage, profilePhoto;

  for await (const part of parts) {
    if (part.fieldname === 'username') {
      username = await part.value;
    } else if (part.fieldname === 'profile_page') {
      profilePage = await part.value;
    } else if (part.fieldname === 'profile_photo') {
      profilePhoto = await part.toBuffer();
    }
  }

  if (!username || !profilePage || !profilePhoto) {
    return reply.status(400).send('Invalid input');
  }

  // Basic input validation
  if (typeof username !== 'string' || typeof profilePage !== 'string') {
    return reply.status(400).send('Invalid input types');
  }

  db.get('SELECT username FROM profiles WHERE username = ?', [username], (err, row) => {
    if (err) {
      return reply.status(500).send('Database error');
    }
    if (row) {
      return reply.status(403).send('Profile already exists, creation forbidden');
    }

    db.run('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)', [username, profilePage, profilePhoto], (err) => {
      if (err) {
        return reply.status(500).send('Database error');
      }
      reply.status(201).send('Profile created successfully');
    });
  });
});

// Route to get a user profile
fastify.get('/profile/:username', (req, reply) => {
  const { username } = req.params;

  db.get('SELECT profile_page FROM profiles WHERE username = ?', [username], (err, row) => {
    if (err) {
      return reply.status(500).send('Database error');
    }
    if (!row) {
      return reply.status(404).send('Profile not found');
    }
    reply.type('text/html').send(row.profile_page);
  });
});

// Route to get a user profile photo
fastify.get('/profile-photo/:username', (req, reply) => {
  const { username } = req.params;

  db.get('SELECT profile_photo FROM profiles WHERE username = ?', [username], (err, row) => {
    if (err) {
      return reply.status(500).send('Database error');
    }
    if (!row) {
      return reply.status(404).send('Profile photo not found');
    }
    reply.type('image/png').send(row.profile_photo);
  });
});

// Start the server
fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});