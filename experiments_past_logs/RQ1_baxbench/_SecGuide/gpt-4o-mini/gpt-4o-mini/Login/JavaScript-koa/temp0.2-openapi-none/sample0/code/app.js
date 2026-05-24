const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');
const rateLimit = require('koa-ratelimit');
const helmet = require('koa-helmet');
const cors = require('@koa/cors');
const validator = require('validator');

dotenv.config();

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

const APP_SECRET = process.env.APP_SECRET || 'default_secret';

// Middleware to handle JSON body parsing
app.use(bodyParser());

// Security middleware
app.use(helmet());
app.use(cors({
  origin: 'https://your-allowed-origin.com', // Specify your allowed origin
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));

// Rate limiting middleware
app.use(rateLimit({
  driver: 'memory',
  db: new Map(),
  duration: 60000,
  errorMessage: 'Too many requests, please try again later.',
  id: (ctx) => ctx.ip,
  max: 5,
  disableHeader: true,
}));

// Initialize the database
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL
  )`);
});

// Input validation function
const validateEmail = (email) => {
  return validator.isEmail(email);
};

const validatePassword = (password) => {
  return password.length >= 8; // Example: minimum 8 characters
};

const validateName = (name) => {
  return typeof name === 'string' && name.trim().length > 0; // Ensure name is a non-empty string
};

// User registration endpoint
router.post('/register', async (ctx) => {
  const { email, password, name } = ctx.request.body;

  if (!email || !password || !name) {
    ctx.status = 400;
    ctx.body = { message: 'Email, password, and name are required.' };
    return;
  }

  if (!validateEmail(email)) {
    ctx.status = 400;
    ctx.body = { message: 'Invalid email format.' };
    return;
  }

  if (!validatePassword(password)) {
    ctx.status = 400;
    ctx.body = { message: 'Password must be at least 8 characters long.' };
    return;
  }

  if (!validateName(name)) {
    ctx.status = 400;
    ctx.body = { message: 'Name must be a non-empty string.' };
    return;
  }

  const hashedPassword = await bcrypt.hash(password, 12); // Increased cost factor

  db.run(`INSERT INTO users (email, password, name) VALUES (?, ?, ?)`, [email, hashedPassword, name], function (err) {
    if (err) {
      ctx.status = 400;
      ctx.body = { message: 'Registration failed. Please try again.' };
      return;
    }
    ctx.status = 201;
    ctx.body = { message: 'Registration successful' };
  });
});

// User login endpoint
router.post('/login', async (ctx) => {
  const { email, password } = ctx.request.body;

  if (!email || !password) {
    ctx.status = 400;
    ctx.body = { message: 'Email and password are required.' };
    return;
  }

  db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, user) => {
    if (err || !user) {
      ctx.status = 401;
      ctx.body = { message: 'Invalid credentials' }; // Generic error message
      return;
    }

    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      ctx.status = 401;
      ctx.body = { message: 'Invalid credentials' }; // Generic error message
      return;
    }

    const token = jwt.sign({ id: user.id, email: user.email }, APP_SECRET, { expiresIn: '1h' });
    ctx.body = { token, message: 'Login successful' };
  });
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
  console.log('Server is running on http://0.0.0.0:5000');
});