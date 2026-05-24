const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const { v4: uuidv4 } = require('uuid');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const cors = require('cors');

dotenv.config();

const app = express();
app.use(express.json());
app.use(helmet());
app.use(cors({
  origin: 'https://your-allowed-origin.com', // Replace with your allowed origin
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

const APP_SECRET = process.env.APP_SECRET;
if (!APP_SECRET) {
  throw new Error('APP_SECRET environment variable is not set');
}

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 50, // stricter limit for sensitive operations
  message: 'Too many requests, please try again later.'
});

app.use(limiter);

let db;

(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE,
      username TEXT UNIQUE,
      password TEXT
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS secrets (
      id TEXT PRIMARY KEY,
      userId TEXT,
      secret TEXT,
      FOREIGN KEY(userId) REFERENCES users(id)
    );
  `);
})();

app.post('/register', async (req, res) => {
  const { email, username, password } = req.body;
  if (!email || !username || !password) {
    return res.status(400).json({ message: 'Invalid data' });
  }

  if (password.length < 8) {
    return res.status(400).json({ message: 'Password must be at least 8 characters long' });
  }

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    const userId = uuidv4();
    await db.run('INSERT INTO users (id, email, username, password) VALUES (?, ?, ?, ?)', [userId, email, username, hashedPassword]);
    res.status(201).json({ message: 'Registration successful' });
  } catch (error) {
    res.status(400).json({ message: 'Email or username already in use or invalid data' });
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
      const token = jwt.sign({ userId: user.id }, APP_SECRET, { expiresIn: '1h' });
      res.status(200).json({ token, message: 'Login successful' });
    } else {
      res.status(401).json({ message: 'Invalid email or password' });
    }
  } catch (error) {
    res.status(401).json({ message: 'Invalid email or password' });
  }
});

app.post('/set_secret', async (req, res) => {
  const { secret } = req.body;
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ message: 'Invalid authentication token' });
  }

  try {
    const decoded = jwt.verify(token, APP_SECRET);
    const secretId = uuidv4();
    await db.run('INSERT INTO secrets (id, userId, secret) VALUES (?, ?, ?)', [secretId, decoded.userId, secret]);
    res.status(200).json({ message: 'Secret has been set successfully' });
  } catch (error) {
    res.status(401).json({ message: 'Invalid authentication token' });
  }
});

app.get('/get_secret', async (req, res) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ message: 'Invalid authentication token' });
  }

  try {
    const decoded = jwt.verify(token, APP_SECRET);
    const secret = await db.get('SELECT secret FROM secrets WHERE userId = ?', [decoded.userId]);
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