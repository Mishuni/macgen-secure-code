import fastify from 'fastify';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';
import helmet from 'fastify-helmet';
import Joi from 'joi';

dotenv.config();

const app = fastify();
const APP_SECRET = process.env.APP_SECRET;
const PORT = 5000;

// Ensure APP_SECRET is set
if (!APP_SECRET) {
  console.error('APP_SECRET environment variable is not set. Terminating application.');
  process.exit(1);
}

// Add security headers
app.register(helmet);

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
      password TEXT,
      name TEXT
    )
  `);
})();

// Helper function to generate JWT
function generateToken(email) {
  return jwt.sign({ email, iat: Math.floor(Date.now() / 1000) }, APP_SECRET, { expiresIn: '1h' });
}

// Input validation schemas
const registerSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(8).required(),
  name: Joi.string().min(1).required()
});

const loginSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(8).required()
});

// Register route
app.post('/register', async (request, reply) => {
  const { error, value } = registerSchema.validate(request.body);

  if (error) {
    return reply.status(400).send({ message: 'Invalid data', details: error.details });
  }

  const { email, password, name } = value;

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    await db.run('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', [email, hashedPassword, name]);
    reply.status(201).send({ message: 'Registration successful' });
  } catch (err) {
    reply.status(400).send({ message: 'Registration failed', error: err.message });
  }
});

// Login route
app.post('/login', async (request, reply) => {
  const { error, value } = loginSchema.validate(request.body);

  if (error) {
    return reply.status(401).send({ message: 'Invalid email or password', details: error.details });
  }

  const { email, password } = value;

  try {
    const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);

    if (user && await bcrypt.compare(password, user.password)) {
      const token = generateToken(email);
      reply.send({ token, message: 'Login successful' });
    } else {
      reply.status(401).send({ message: 'Invalid email or password' });
    }
  } catch (err) {
    reply.status(500).send({ message: 'Internal server error', error: err.message });
  }
});

// Start server
app.listen({ port: PORT, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});