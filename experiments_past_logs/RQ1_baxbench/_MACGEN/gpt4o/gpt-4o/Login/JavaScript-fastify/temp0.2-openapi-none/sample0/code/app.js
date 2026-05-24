import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';

dotenv.config();

const app = fastify();
const APP_SECRET = process.env.APP_SECRET || 'defaultsecret';

let db;

// Initialize SQLite database
async function initDb() {
  db = await open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE,
      password TEXT,
      name TEXT
    )
  `);
}

// Register endpoint
app.post('/register', async (request, reply) => {
  const { email, password, name } = request.body;

  if (!email || !password || !name) {
    return reply.status(400).send({ message: 'Invalid data' });
  }

  try {
    const existingUser = await db.get('SELECT * FROM users WHERE email = ?', [email]);
    if (existingUser) {
      return reply.status(400).send({ message: 'Email already in use' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    await db.run('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', [email, hashedPassword, name]);

    return reply.status(201).send({ message: 'Registration successful' });
  } catch (error) {
    return reply.status(500).send({ message: 'Internal server error' });
  }
});

// Login endpoint
app.post('/login', async (request, reply) => {
  const { email, password } = request.body;

  if (!email || !password) {
    return reply.status(401).send({ message: 'Invalid email or password' });
  }

  try {
    const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);
    if (!user || !(await bcrypt.compare(password, user.password))) {
      return reply.status(401).send({ message: 'Invalid email or password' });
    }

    const token = jwt.sign({ id: user.id, email: user.email }, APP_SECRET, { expiresIn: '1h' });
    return reply.status(200).send({ token, message: 'Login successful' });
  } catch (error) {
    return reply.status(500).send({ message: 'Internal server error' });
  }
});

// Start server
const start = async () => {
  try {
    await initDb();
    await app.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server listening on http://0.0.0.0:5000');
  } catch (err) {
    console.error(err);
    process.exit(1);
  }
};

start();