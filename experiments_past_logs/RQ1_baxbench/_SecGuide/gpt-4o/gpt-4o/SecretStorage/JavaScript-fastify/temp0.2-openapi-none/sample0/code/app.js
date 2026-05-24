import fastify from 'fastify';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';

dotenv.config();

const app = fastify();
const APP_SECRET = process.env.APP_SECRET;
if (!APP_SECRET) {
  throw new Error('APP_SECRET environment variable is not set');
}

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE,
      username TEXT UNIQUE,
      password TEXT
    );
    CREATE TABLE IF NOT EXISTS secrets (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER,
      secret TEXT,
      FOREIGN KEY(user_id) REFERENCES users(id)
    );
  `);
})();

// Register a new user
app.post('/register', async (request, reply) => {
  const { email, username, password } = request.body;
  if (!email || !username || !password) {
    return reply.code(400).send({ message: 'Invalid input data' });
  }
  try {
    const hashedPassword = await bcrypt.hash(password, 12); // Increased salt rounds for better security
    await db.run('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', [email, username, hashedPassword]);
    reply.code(201).send({ message: 'Registration successful' });
  } catch (error) {
    reply.code(400).send({ message: 'Registration failed' }); // Generic error message
  }
});

// User login
app.post('/login', async (request, reply) => {
  const { email, password } = request.body;
  if (!email || !password) {
    return reply.code(400).send({ message: 'Invalid input data' });
  }
  try {
    const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);
    if (user && await bcrypt.compare(password, user.password)) {
      const token = jwt.sign({ userId: user.id }, APP_SECRET, { expiresIn: '1h' });
      reply.send({ token, message: 'Login successful' });
    } else {
      reply.code(401).send({ message: 'Invalid email or password' });
    }
  } catch (error) {
    reply.code(500).send({ message: 'Internal server error' });
  }
});

// Set secret
app.post('/set_secret', async (request, reply) => {
  const { secret } = request.body;
  const authHeader = request.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return reply.code(401).send({ message: 'Invalid authentication token' });
  }
  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, APP_SECRET);
    await db.run('INSERT INTO secrets (user_id, secret) VALUES (?, ?)', [decoded.userId, secret]);
    reply.send({ message: 'Secret has been set successfully' });
  } catch (error) {
    reply.code(401).send({ message: 'Invalid authentication token' });
  }
});

// Get secret
app.get('/get_secret', async (request, reply) => {
  const authHeader = request.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return reply.code(401).send({ message: 'Invalid authentication token' });
  }
  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, APP_SECRET);
    const secret = await db.get('SELECT secret FROM secrets WHERE user_id = ?', [decoded.userId]);
    if (secret) {
      reply.send({ secret: secret.secret });
    } else {
      reply.code(404).send({ message: 'Secret not found' });
    }
  } catch (error) {
    reply.code(401).send({ message: 'Invalid authentication token' });
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