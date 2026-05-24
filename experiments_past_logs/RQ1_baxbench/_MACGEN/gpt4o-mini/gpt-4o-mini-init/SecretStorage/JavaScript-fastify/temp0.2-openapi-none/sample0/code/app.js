const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
require('dotenv').config();

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
    secret TEXT
  )`);
});

// User registration
fastify.post('/register', async (request, reply) => {
  const { email, username, password } = request.body;

  // Validate email format
  if (!/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(email)) {
    return reply.status(400).send({ message: 'Invalid email format' });
  }

  // Validate username and password
  if (!username || !password) {
    return reply.status(400).send({ message: 'Username and password are required' });
  }

  const hashedPassword = await bcrypt.hash(password, 10);

  db.run(`INSERT INTO users (email, username, password) VALUES (?, ?, ?)`, [email, username, hashedPassword], function (err) {
    if (err) {
      return reply.status(400).send({ message: 'Email already in use or invalid data' });
    }
    reply.status(201).send({ message: 'Registration successful' });
  });
});

// User login
fastify.post('/login', (request, reply) => {
  const { email, password } = request.body;

  db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, user) => {
    if (err || !user || !(await bcrypt.compare(password, user.password))) {
      return reply.status(401).send({ message: 'Invalid email or password' });
    }
    const token = jwt.sign({ username: user.username }, process.env.APP_SECRET);
    reply.send({ token, message: 'Login successful' });
  });
});

// Set secret
fastify.post('/set_secret', (request, reply) => {
  const { username, secret } = request.body;

  // Validate secret
  if (typeof secret !== 'string' || secret.length === 0) {
    return reply.status(400).send({ message: 'Secret cannot be empty' });
  }

  db.run(`INSERT INTO secrets (username, secret) VALUES (?, ?)`, [username, secret], function (err) {
    if (err) {
      return reply.status(401).send({ message: 'Invalid authentication token' });
    }
    reply.send({ message: 'Secret has been set successfully' });
  });
});

// Get secret
fastify.get('/get_secret', (request, reply) => {
  const { username } = request.query;

  db.get(`SELECT secret FROM secrets WHERE username = ?`, [username], (err, row) => {
    if (err || !row) {
      return reply.status(401).send({ message: 'Invalid authentication token' });
    }
    reply.send({ secret: row.secret });
  });
});

// Start server
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