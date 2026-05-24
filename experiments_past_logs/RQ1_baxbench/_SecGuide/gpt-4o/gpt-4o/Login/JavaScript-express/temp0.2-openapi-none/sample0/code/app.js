const express = require('express');
const bcrypt = require('bcrypt');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');
const fs = require('fs');
const https = require('https');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const cors = require('cors');

dotenv.config();

const app = express();
app.use(express.json());
app.use(helmet());

// CORS configuration
const corsOptions = {
  origin: 'https://your-allowed-origin.com', // Update with your allowed origin
  optionsSuccessStatus: 200
};
app.use(cors(corsOptions));

const APP_SECRET = process.env.APP_SECRET;
if (!APP_SECRET) {
  console.error('APP_SECRET environment variable is not set.');
  process.exit(1);
}

const PASSWORD_MIN_LENGTH = 12; // Increased minimum length
const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).+$/; // Added special character requirement

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.'
});

app.use(limiter); // Apply rate limiting to all endpoints

let db;
(async () => {
  db = await sqlite.open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT,
    name TEXT
  )`);
})();

function generateToken(user) {
  return jwt.sign({ id: user.id, email: user.email }, APP_SECRET, { expiresIn: '1h' });
}

app.post('/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ message: 'Email and password are required' });
  }

  try {
    const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);
    if (user && await bcrypt.compare(password, user.password)) {
      const token = generateToken(user);
      return res.status(200).json({ token, message: 'Login successful' });
    } else {
      return res.status(401).json({ message: 'Invalid email or password' });
    }
  } catch (error) {
    console.error('Error during login:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
});

app.post('/register', async (req, res) => {
  const { email, password, name } = req.body;
  if (!email || !password || !name) {
    return res.status(400).json({ message: 'Email, password, and name are required' });
  }

  if (password.length < PASSWORD_MIN_LENGTH || !PASSWORD_REGEX.test(password)) {
    return res.status(400).json({ message: 'Password does not meet complexity requirements' });
  }

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    await db.run('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', [email, hashedPassword, name]);
    return res.status(201).json({ message: 'Registration successful' });
  } catch (error) {
    if (error.code === 'SQLITE_CONSTRAINT') {
      return res.status(400).json({ message: 'Email already in use or invalid data' });
    }
    console.error('Error during registration:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
});

const options = {
  key: fs.readFileSync('server.key'),
  cert: fs.readFileSync('server.cert')
};

https.createServer(options, app).listen(5000, '127.0.0.1', () => {
  console.log('Server is running on https://127.0.0.1:5000');
});