const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');
const DOMPurify = require('dompurify');
const { JSDOM } = require('jsdom');
require('dotenv').config();

const db = new sqlite3.Database('db.sqlite3');

// Create the profiles table if it doesn't exist
db.run(`CREATE TABLE IF NOT EXISTS profiles (
  username TEXT PRIMARY KEY,
  profile_page TEXT,
  profile_photo TEXT
)`);

fastify.register(multipart);

// Add a new user profile
fastify.post('/add_profile', async (request, reply) => {
  const data = await request.file();
  const { username, profile_page } = request.body;

  if (!username || !profile_page || !data) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  // Validate username and profile_page to prevent XSS
  const sanitizedUsername = username.replace(/<[^>]*>/g, '');
  const sanitizedProfilePage = DOMPurify.sanitize(profile_page);

  // Validate file type and size
  const allowedTypes = ['image/png', 'image/jpeg', 'image/gif'];
  const maxFileSize = 5 * 1024 * 1024; // 5 MB

  if (!allowedTypes.includes(data.mimetype) || data.file.size > maxFileSize) {
    return reply.status(400).send({ error: 'Invalid file type or size' });
  }

  const profilePhotoPath = path.join(__dirname, 'uploads', `${sanitizedUsername}_${Date.now()}_${path.basename(data.filename)}`);
  const writeStream = fs.createWriteStream(profilePhotoPath);

  data.file.pipe(writeStream);

  writeStream.on('finish', () => {
    db.get('SELECT username FROM profiles WHERE username = ?', [sanitizedUsername], (err, row) => {
      if (err) {
        fs.unlinkSync(profilePhotoPath); // Clean up the uploaded file
        return reply.status(500).send({ error: 'Database error' });
      }
      if (row) {
        fs.unlinkSync(profilePhotoPath); // Clean up the uploaded file
        return reply.status(403).send({ error: 'Profile already exists, creation forbidden' });
      }

      db.run('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)', [sanitizedUsername, sanitizedProfilePage, profilePhotoPath], function(err) {
        if (err) {
          fs.unlinkSync(profilePhotoPath); // Clean up the uploaded file
          return reply.status(500).send({ error: 'Database error' });
        }
        reply.status(201).send({ message: 'Profile created successfully' });
      });
    });
  });

  writeStream.on('error', (err) => {
    return reply.status(500).send({ error: 'File upload error' });
  });
});

// Get user profile
fastify.get('/profile/:username', (request, reply) => {
  const { username } = request.params;

  db.get('SELECT profile_page FROM profiles WHERE username = ?', [username], (err, row) => {
    if (err) {
      return reply.status(500).send({ error: 'Database error' });
    }
    if (!row) {
      return reply.status(404).send({ error: 'Profile not found' });
    }
    reply.type('text/html').send(row.profile_page);
  });
});

// Get user profile photo
fastify.get('/profile-photo/:username', (request, reply) => {
  const { username } = request.params;

  db.get('SELECT profile_photo FROM profiles WHERE username = ?', [username], (err, row) => {
    if (err) {
      return reply.status(500).send({ error: 'Database error' });
    }
    if (!row) {
      return reply.status(404).send({ error: 'Profile photo not found' });
    }
    reply.sendFile(row.profile_photo);
  });
});

// Start the server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();