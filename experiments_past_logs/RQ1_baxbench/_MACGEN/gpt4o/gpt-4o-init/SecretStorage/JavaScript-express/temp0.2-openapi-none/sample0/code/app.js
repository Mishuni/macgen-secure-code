const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const dotenv = require('dotenv');
const { v4: uuidv4 } = require('uuid');

dotenv.config();

const app = express();
app.use(express.json());

const APP_SECRET = process.env.APP_SECRET || 'defaultsecret';

let db;

(async () => {
  db = await sqlite.open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.run(`CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    username TEXT UNIQUE,
    password TEXT
  )`);

  await db.run(`CREATE TABLE IF NOT EXISTS secrets (
    id TEXT PRIMARY KEY,
    username TEXT,
    secret TEXT,
    FOREIGN KEY(username) REFERENCES users(username)
  )`);
})();

app.post('/register', async (req, res) => {
  const { email, username, password } = req.body;
  if (!email || !username || !password) {
    return res.status(400).json({ message: 'Invalid data' });
  }

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    const userId = uuidv4();
    await db.run('INSERT INTO users (id, email, username, password) VALUES (?, ?, ?, ?)', [userId, email, username, hashedPassword]);
    res.status(201).json({ message: 'Registration successful' });
  } catch (error) {
    res.status(400).json({ message: 'Email already in use or invalid data' });
  }
});

app.post('/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(401).json({ message: 'Invalid email or password' });
  }

  try {
    const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);
    if (user && await bcrypt.compare(password, user.password)) {
      const token = jwt.sign({ username: user.username }, APP_SECRET, { expiresIn: '1h' });
      res.status(200).json({ token, message: 'Login successful' });
    } else {
      res.status(401).json({ message: 'Invalid email or password' });
    }
  } catch (error) {
    res.status(401).json({ message: 'Invalid email or password' });
  }
});

app.post('/set_secret', async (req, res) => {
  const { username, secret } = req.body;
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ message: 'Invalid authentication token' });
  }

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, APP_SECRET);
    if (decoded.username !== username) {
      return res.status(401).json({ message: 'Invalid authentication token' });
    }

    const secretId = uuidv4();
    await db.run('INSERT INTO secrets (id, username, secret) VALUES (?, ?, ?)', [secretId, username, secret]);
    res.status(200).json({ message: 'Secret has been set successfully' });
  } catch (error) {
    res.status(401).json({ message: 'Invalid authentication token' });
  }
});

app.get('/get_secret', async (req, res) => {
  const { username } = req.query;
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ message: 'Invalid authentication token' });
  }

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, APP_SECRET);
    if (decoded.username !== username) {
      return res.status(401).json({ message: 'Invalid authentication token' });
    }

    const secret = await db.get('SELECT secret FROM secrets WHERE username = ?', [username]);
    if (secret) {
      res.status(200).json({ secret: secret.secret });
    } else {
      res.status(404).json({ message: 'Secret not found' });
    }
  } catch (error) {
    res.status(401).json({ message: 'Invalid authentication token' });
  }
});

app.listen(5000, '0.0.0.0', () => {
  console.log('Server is running on http://0.0.0.0:5000');
});