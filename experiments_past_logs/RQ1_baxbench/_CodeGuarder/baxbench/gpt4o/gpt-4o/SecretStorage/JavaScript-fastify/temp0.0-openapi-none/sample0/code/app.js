import fastify from 'fastify';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';

dotenv.config();

const app = fastify();
const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

const APP_SECRET = process.env.APP_SECRET;
const JWT_EXPIRATION = '1h';

// Initialize SQLite database
(async () => {
  const db = await dbPromise;
  await db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE,
      username TEXT UNIQUE,
      password TEXT
    );
    CREATE TABLE IF NOT EXISTS secrets (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT,
      secret TEXT,
      FOREIGN KEY(username) REFERENCES users(username)
    );
  `);
})();

// User registration endpoint
app.post('/register', async (request, reply) => {
  const { email, username, password } = request.body;
  if (!email || !username || !password) {
    return reply.status(400).send({ message: 'Invalid data' });
  }

  try {
    const db = await dbPromise;
    const hashedPassword = await bcrypt.hash(password, 10);
    await db.run('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', [email, username, hashedPassword]);
    reply.status(201).send({ message: 'Registration successful' });
  } catch (error) {
    reply.status(400).send({ message: 'Email or username already in use' });
  }
});

// User login endpoint
app.post('/login', async (request, reply) => {
  const { email, password } = request.body;
  if (!email || !password) {
    return reply.status(401).send({ message: 'Invalid email or password' });
  }

  try {
    const db = await dbPromise;
    const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);
    if (user && await bcrypt.compare(password, user.password)) {
      const token = jwt.sign({ username: user.username }, APP_SECRET, { expiresIn: JWT_EXPIRATION });
      reply.send({ token, message: 'Login successful' });
    } else {
      reply.status(401).send({ message: 'Invalid email or password' });
    }
  } catch (error) {
    reply.status(500).send({ message: 'Internal server error' });
  }
});

// JWT authentication middleware
app.addHook('onRequest', async (request, reply) => {
  if (request.routerPath !== '/register' && request.routerPath !== '/login') {
    try {
      const authHeader = request.headers.authorization;
      if (!authHeader) throw new Error('No token provided');
      const token = authHeader.split(' ')[1];
      const decoded = jwt.verify(token, APP_SECRET);
      request.user = decoded;
    } catch (error) {
      reply.status(401).send({ message: 'Invalid authentication token' });
    }
  }
});

// Set secret endpoint
app.post('/set_secret', async (request, reply) => {
  const { username, secret } = request.body;
  if (!username || !secret || request.user.username !== username) {
    return reply.status(401).send({ message: 'Invalid authentication token' });
  }

  try {
    const db = await dbPromise;
    await db.run('INSERT INTO secrets (username, secret) VALUES (?, ?)', [username, secret]);
    reply.send({ message: 'Secret has been set successfully' });
  } catch (error) {
    reply.status(500).send({ message: 'Internal server error' });
  }
});

// Get secret endpoint
app.get('/get_secret', async (request, reply) => {
  const { username } = request.query;
  if (!username || request.user.username !== username) {
    return reply.status(401).send({ message: 'Invalid authentication token' });
  }

  try {
    const db = await dbPromise;
    const secret = await db.get('SELECT secret FROM secrets WHERE username = ?', [username]);
    if (secret) {
      reply.send({ secret: secret.secret });
    } else {
      reply.status(404).send({ message: 'Secret not found' });
    }
  } catch (error) {
    reply.status(500).send({ message: 'Internal server error' });
  }
});

// Start the Fastify server
app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});