const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');
const { body, query, validationResult } = require('express-validator');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const cors = require('cors');

dotenv.config();

const db = new sqlite3.Database('db.sqlite3');

// Create tables if they don't exist
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    username TEXT UNIQUE,
    password TEXT
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS secrets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    secret TEXT,
    FOREIGN KEY (username) REFERENCES users (username)
  )`);
});

// Password complexity check
const isValidPassword = (password) => {
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
  return passwordRegex.test(password);
};

// Middleware for security headers
fastify.register(helmet);

// CORS configuration
fastify.register(cors, {
  origin: 'https://your-allowed-origin.com', // Change to your allowed origin
});

// User registration
fastify.post('/register', async (request, reply) => {
  const { email, username, password } = request.body;

  if (!email || !username || !password || !isValidPassword(password)) {
    return reply.status(400).send({ message: 'Invalid registration data' });
  }

  const hashedPassword = await bcrypt.hash(password, 10);

  db.run(`INSERT INTO users (email, username, password) VALUES (?, ?, ?)`, [email, username, hashedPassword], function(err) {
    if (err) {
      return reply.status(400).send({ message: 'Email already in use' });
    }
    reply.status(201).send({ message: 'Registration successful' });
  });
});

// User login
fastify.post('/login', async (request, reply) => {
  const { email, password } = request.body;

  db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, user) => {
    if (err || !user || !(await bcrypt.compare(password, user.password))) {
      return reply.status(401).send({ message: 'Invalid credentials' });
    }

    const token = jwt.sign({ username: user.username }, process.env.APP_SECRET, { expiresIn: '1h' });
    reply.send({ token, message: 'Login successful' });
  });
});

// Set secret
fastify.post('/set_secret', async (request, reply) => {
  const { secret } = request.body;
  const token = request.headers['authorization']?.split(' ')[1];

  if (!token) {
    return reply.status(401).send({ message: 'Invalid authentication token' });
  }

  try {
    const decoded = jwt.verify(token, process.env.APP_SECRET);
    const username = decoded.username;

    db.run(`INSERT INTO secrets (username, secret) VALUES (?, ?)`, [username, secret], function(err) {
      if (err) {
        return reply.status(400).send({ message: 'Error saving secret' });
      }
      reply.send({ message: 'Secret has been set successfully' });
    });
  } catch (err) {
    return reply.status(401).send({ message: 'Invalid authentication token' });
  }
});

// Get secret
fastify.get('/get_secret', async (request, reply) => {
  const token = request.headers['authorization']?.split(' ')[1];

  if (!token) {
    return reply.status(401).send({ message: 'Invalid authentication token' });
  }

  try {
    const decoded = jwt.verify(token, process.env.APP_SECRET);
    const username = decoded.username;

    db.get(`SELECT secret FROM secrets WHERE username = ?`, [username], (err, row) => {
      if (err || !row) {
        return reply.status(404).send({ message: 'Secret not found' });
      }
      reply.send({ secret: row.secret });
    });
  } catch (err) {
    return reply.status(401).send({ message: 'Invalid authentication token' });
  }
});

// Start server
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