const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');
const { v4: uuidv4 } = require('uuid');
const validator = require('validator');
const helmet = require('koa-helmet');
const rateLimit = require('koa-ratelimit');

dotenv.config();

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

const APP_SECRET = process.env.APP_SECRET || 'default_secret';

// Middleware to handle JSON body parsing
app.use(bodyParser());

// Security middleware
app.use(helmet());

// Rate limiting middleware
app.use(rateLimit({
  driver: 'memory',
  db: new Map(),
  duration: 60000,
  errorMessage: 'Too many requests, please try again later.',
  id: (ctx) => ctx.ip,
  max: 5,
  disable: (ctx) => ctx.path !== '/login' && ctx.path !== '/register',
}));

// Initialize the database
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    username TEXT UNIQUE,
    password TEXT
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS secrets (
    id TEXT PRIMARY KEY,
    userId TEXT,
    secret TEXT,
    FOREIGN KEY (userId) REFERENCES users (id)
  )`);
});

// Middleware to validate JWT
const authenticate = (ctx, next) => {
  const token = ctx.headers['authorization']?.split(' ')[1];
  if (!token) {
    ctx.status = 401;
    ctx.body = { message: 'Authentication token is required' };
    return;
  }
  try {
    const decoded = jwt.verify(token, APP_SECRET);
    ctx.state.user = decoded;
    return next();
  } catch (err) {
    ctx.status = 401;
    ctx.body = { message: 'Invalid authentication token' };
  }
};

// User registration
router.post('/register', async (ctx) => {
  const { email, username, password } = ctx.request.body;

  if (!email || !username || !password || !validator.isEmail(email) || password.length < 8 || !/(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[A-Z])/.test(password)) {
    ctx.status = 400;
    ctx.body = { message: 'Invalid email, username, or password' };
    return;
  }

  const hashedPassword = await bcrypt.hash(password, 10);
  const userId = uuidv4();

  db.run(`INSERT INTO users (id, email, username, password) VALUES (?, ?, ?, ?)`, [userId, email, username, hashedPassword], function(err) {
    if (err) {
      ctx.status = 400;
      ctx.body = { message: 'Email or username already in use' };
      return;
    }
    ctx.status = 201;
    ctx.body = { message: 'Registration successful' };
  });
});

// User login
router.post('/login', async (ctx) => {
  const { email, password } = ctx.request.body;

  db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, user) => {
    if (err || !user || !(await bcrypt.compare(password, user.password))) {
      ctx.status = 401;
      ctx.body = { message: 'Invalid credentials' };
      return;
    }

    const token = jwt.sign({ userId: user.id }, APP_SECRET, { expiresIn: '1h' });
    ctx.body = { token, message: 'Login successful' };
  });
});

// Set secret
router.post('/set_secret', authenticate, (ctx) => {
  const { secret } = ctx.request.body;
  const userId = ctx.state.user.userId;

  if (!secret) {
    ctx.status = 400;
    ctx.body = { message: 'Secret is required' };
    return;
  }

  const secretId = uuidv4();
  db.run(`INSERT INTO secrets (id, userId, secret) VALUES (?, ?, ?)`, [secretId, userId, secret], function(err) {
    if (err) {
      ctx.status = 400;
      ctx.body = { message: 'Error setting secret' };
      return;
    }
    ctx.body = { message: 'Secret has been set successfully' };
  });
});

// Get secret
router.get('/get_secret', authenticate, (ctx) => {
  const userId = ctx.state.user.userId;

  db.get(`SELECT secret FROM secrets WHERE userId = ?`, [userId], (err, row) => {
    if (err || !row) {
      ctx.status = 404;
      ctx.body = { message: 'Secret not found' };
      return;
    }
    ctx.body = { secret: row.secret };
  });
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
  console.log('Server is running on http://0.0.0.0:5000');
});