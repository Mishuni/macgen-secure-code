import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';

dotenv.config();

const app = fastify();
const db = new sqlite3.Database('db.sqlite3');

// Initialize the database
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL
  )`);
});

// Helper function to generate JWT
function generateToken(user) {
  const payload = { id: user.id, email: user.email };
  return jwt.sign(payload, process.env.APP_SECRET, { expiresIn: '1h' });
}

// User registration endpoint
app.post('/register', async (request, reply) => {
  const { email, password, name } = request.body;

  if (!email || !password || !name) {
    return reply.status(400).send({ message: 'Invalid data' });
  }

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    db.run(
      `INSERT INTO users (email, password, name) VALUES (?, ?, ?)`,
      [email, hashedPassword, name],
      function (err) {
        if (err) {
          return reply.status(400).send({ message: 'Email already in use' });
        }
        reply.status(201).send({ message: 'Registration successful' });
      }
    );
  } catch (error) {
    reply.status(500).send({ message: 'Internal server error' });
  }
});

// User login endpoint
app.post('/login', async (request, reply) => {
  const { email, password } = request.body;

  if (!email || !password) {
    return reply.status(400).send({ message: 'Invalid email or password' });
  }

  db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, user) => {
    if (err || !user) {
      return reply.status(401).send({ message: 'Invalid email or password' });
    }

    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      return reply.status(401).send({ message: 'Invalid email or password' });
    }

    const token = generateToken(user);
    reply.send({ token, message: 'Login successful' });
  });
});

// Start the server
app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});