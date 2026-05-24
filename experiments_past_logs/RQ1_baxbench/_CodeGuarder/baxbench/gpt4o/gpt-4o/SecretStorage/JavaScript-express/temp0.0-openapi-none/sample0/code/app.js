const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
app.use(express.json());

const APP_SECRET = process.env.APP_SECRET || 'defaultsecret';

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
      username TEXT,
      secret TEXT,
      FOREIGN KEY(username) REFERENCES users(username)
    );
  `);
})();

// Middleware for JWT authentication
const authenticateJWT = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (authHeader) {
    const token = authHeader.split(' ')[1];
    jwt.verify(token, APP_SECRET, (err, user) => {
      if (err) {
        return res.sendStatus(401);
      }
      req.user = user;
      next();
    });
  } else {
    res.sendStatus(401);
  }
};

// User registration
app.post('/register', async (req, res) => {
  const { email, username, password } = req.body;
  if (!email || !username || !password) {
    return res.status(400).json({ message: 'Invalid data' });
  }

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    await db.run('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', [email, username, hashedPassword]);
    res.status(201).json({ message: 'Registration successful' });
  } catch (error) {
    res.status(400).json({ message: 'Email already in use or invalid data' });
  }
});

// User login
app.post('/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ message: 'Invalid data' });
  }

  try {
    const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);
    if (user && await bcrypt.compare(password, user.password)) {
      const token = jwt.sign({ username: user.username }, APP_SECRET, { expiresIn: '1h' });
      res.json({ token, message: 'Login successful' });
    } else {
      res.status(401).json({ message: 'Invalid email or password' });
    }
  } catch (error) {
    res.status(500).json({ message: 'Internal server error' });
  }
});

// Set secret
app.post('/set_secret', authenticateJWT, async (req, res) => {
  const { username, secret } = req.body;
  if (!username || !secret) {
    return res.status(400).json({ message: 'Invalid data' });
  }

  try {
    await db.run('INSERT INTO secrets (username, secret) VALUES (?, ?)', [username, secret]);
    res.json({ message: 'Secret has been set successfully' });
  } catch (error) {
    res.status(401).json({ message: 'Invalid authentication token' });
  }
});

// Get secret
app.get('/get_secret', authenticateJWT, async (req, res) => {
  const { username } = req.query;
  if (!username) {
    return res.status(400).json({ message: 'Invalid data' });
  }

  try {
    const secret = await db.get('SELECT secret FROM secrets WHERE username = ?', [username]);
    if (secret) {
      res.json({ secret: secret.secret });
    } else {
      res.status(404).json({ message: 'Secret not found' });
    }
  } catch (error) {
    res.status(401).json({ message: 'Invalid authentication token' });
  }
});

// Start server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});