const fastify = require('fastify')();
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const escapeHTML = require('escape-html');

// Initialize SQLite database
const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

// Create the profiles table if it doesn't exist
dbPromise.then(db => {
  return db.exec(`CREATE TABLE IF NOT EXISTS profiles (
    username TEXT PRIMARY KEY,
    profile_page TEXT,
    profile_photo BLOB
  )`);
});

// Middleware for handling multipart/form-data
fastify.register(require('@fastify/multipart'));

// Add a new user profile
fastify.post('/add_profile', async (request, reply) => {
  const data = await request.multipart();
  const profileData = {};
  
  data.on('field', (field, value) => {
    profileData[field] = value;
  });

  const profilePhoto = await new Promise((resolve, reject) => {
    data.on('file', (field, file) => {
      const chunks = [];
      file.on('data', chunk => {
        chunks.push(chunk);
      });
      file.on('end', () => {
        resolve(Buffer.concat(chunks));
      });
      file.on('error', reject);
    });
  });

  data.on('end', async () => {
    const db = await dbPromise;
    try {
      const safeProfilePage = escapeHTML(profileData.profile_page);
      await db.run(`INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)`, 
        [profileData.username, safeProfilePage, profilePhoto]);
      reply.status(201).send({ message: 'Profile created successfully' });
    } catch (err) {
      if (err.code === 'SQLITE_CONSTRAINT') {
        reply.status(403).send({ error: 'Profile already exists, creation forbidden' });
      } else {
        reply.status(400).send({ error: 'Invalid input' });
      }
    }
  });
});

// Get user profile
fastify.get('/profile/:username', async (request, reply) => {
  const { username } = request.params;
  const db = await dbPromise;
  const row = await db.get(`SELECT profile_page FROM profiles WHERE username = ?`, [username]);
  
  if (!row) {
    return reply.status(404).send({ error: 'Profile not found' });
  }
  reply.type('text/html').send(row.profile_page);
});

// Get user profile photo
fastify.get('/profile-photo/:username', async (request, reply) => {
  const { username } = request.params;
  const db = await dbPromise;
  const row = await db.get(`SELECT profile_photo FROM profiles WHERE username = ?`, [username]);
  
  if (!row) {
    return reply.status(404).send({ error: 'Profile photo not found' });
  }
  reply.type('image/png').send(row.profile_photo);
});

// Start the server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    console.log('server is running on http://0.0.0.0:5000');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();