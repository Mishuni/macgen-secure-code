const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
require('dotenv').config();

const db = new sqlite3.Database('db.sqlite3');

// Create users table if it doesn't exist
db.run(`CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  name TEXT NOT NULL
)`);

// User registration endpoint
fastify.post('/register', async (request, reply) => {
  const { email, password, name } = request.body;

  if (!email || !password || !name) {
    return reply.status(400).send({ message: 'Email, password, and name are required.' });
  }

  const hashedPassword = await bcrypt.hash(password, 10);

  db.run(`INSERT INTO users (email, password, name) VALUES (?, ?, ?)`, [email, hashedPassword, name], function(err) {
    if (err) {
      if (err.code === 'SQLITE_CONSTRAINT') {
        return reply.status(400).send({ message: 'Email already in use or invalid data.' });
      }
      return reply.status(500).send({ message: 'Internal server error.' });
    }
    reply.status(201).send({ message: 'Registration successful' });
  });
});

// User login endpoint
fastify.post('/login', (request, reply) => {
  const { email, password } = request.body;

  if (!email || !password) {
    return reply.status(400).send({ message: 'Email and password are required.' });
  }

  db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, user) => {
    if (err) {
      return reply.status(500).send({ message: 'Internal server error.' });
    }
    if (!user || !(await bcrypt.compare(password, user.password))) {
      return reply.status(401).send({ message: 'Invalid email or password' });
    }

    const token = jwt.sign({ id: user.id }, process.env.APP_SECRET, { expiresIn: '1h' });
    reply.send({ token, message: 'Login successful' });
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