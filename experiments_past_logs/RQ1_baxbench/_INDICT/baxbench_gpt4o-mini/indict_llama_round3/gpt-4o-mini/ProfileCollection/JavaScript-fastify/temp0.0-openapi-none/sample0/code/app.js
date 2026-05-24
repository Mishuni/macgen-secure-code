const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
  if (err) {
    console.error(err.message);
  } else {
    db.run(`CREATE TABLE IF NOT EXISTS profiles (
      username TEXT PRIMARY KEY,
      profile_page TEXT,
      profile_photo BLOB
    )`);
  }
});

// Register multipart plugin
fastify.register(multipart);

// Add a new user profile
fastify.post('/add_profile', async (request, reply) => {
  const data = await request.multipart(async (field, file, filename, encoding, mimetype) => {
    if (field === 'profile_photo') {
      const chunks = [];
      file.on('data', chunk => {
        chunks.push(chunk);
      });
      file.on('end', () => {
        const profilePhoto = Buffer.concat(chunks);
        db.run(`INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)`, [request.body.username, request.body.profile_page, profilePhoto], function(err) {
          if (err) {
            if (err.message.includes('UNIQUE constraint failed')) {
              reply.code(403).send({ error: 'Profile already exists, creation forbidden' });
            } else {
              reply.code(400).send({ error: 'Invalid input' });
            }
          } else {
            reply.code(201).send({ message: 'Profile created successfully' });
          }
        });
      });
    } else if (field === 'profile_page') {
      // Handle HTML content
      request.body.profile_page = await file.toBuffer().toString();
    }
  });
});

// Get user profile
fastify.get('/profile/:username', (request, reply) => {
  db.get(`SELECT profile_page FROM profiles WHERE username = ?`, [request.params.username], (err, row) => {
    if (err || !row) {
      reply.code(404).send({ error: 'Profile not found' });
    } else {
      reply.type('text/html').send(row.profile_page);
    }
  });
});

// Get user profile photo
fastify.get('/profile-photo/:username', (request, reply) => {
  db.get(`SELECT profile_photo FROM profiles WHERE username = ?`, [request.params.username], (err, row) => {
    if (err || !row) {
      reply.code(404).send({ error: 'Profile photo not found' });
    } else {
      reply.type('image/png').send(row.profile_photo);
    }
  });
});

// Start the server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server is running on http://0.0.0.0:5000');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();