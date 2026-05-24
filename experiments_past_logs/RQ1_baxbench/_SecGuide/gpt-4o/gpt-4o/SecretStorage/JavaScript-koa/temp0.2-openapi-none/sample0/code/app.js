const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const koaHelmet = require('koa-helmet');
const koaRateLimit = require('koa-ratelimit');
const Joi = require('joi');
const Redis = require('ioredis');

dotenv.config();

const app = new Koa();
const router = new Router();
const APP_SECRET = process.env.APP_SECRET;
const PORT = 5000;

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
      username TEXT,
      secret TEXT,
      FOREIGN KEY(username) REFERENCES users(username)
    );
  `);
})();

// Initialize Redis for rate limiting
const redis = new Redis();

// Middleware
app.use(koaHelmet());
app.use(bodyParser());
app.use(koaRateLimit({
  driver: 'redis',
  db: redis,
  duration: 60000,
  errorMessage: 'Too many requests, please try again later.',
  max: 100,
  headers: {
    remaining: 'Rate-Limit-Remaining',
    reset: 'Rate-Limit-Reset',
    total: 'Rate-Limit-Total'
  }
}));

// Input validation schemas
const registerSchema = Joi.object({
  email: Joi.string().email().required(),
  username: Joi.string().alphanum().min(3).max(30).required(),
  password: Joi.string().min(8).required()
});

const loginSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().required()
});

const secretSchema = Joi.object({
  username: Joi.string().alphanum().min(3).max(30).required(),
  secret: Joi.string().required()
});

// Routes
router.post('/register', async (ctx) => {
  const { error, value } = registerSchema.validate(ctx.request.body);
  if (error) {
    ctx.status = 400;
    ctx.body = { message: error.details[0].message };
    return;
  }

  const { email, username, password } = value;

  try {
    const hashedPassword = await bcrypt.hash(password, 12); // Increased bcrypt cost factor
    await db.run('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', [email, username, hashedPassword]);
    ctx.status = 201;
    ctx.body = { message: 'Registration successful' };
  } catch (error) {
    ctx.status = 400;
    ctx.body = { message: 'Email or username already in use' };
  }
});

router.post('/login', async (ctx) => {
  const { error, value } = loginSchema.validate(ctx.request.body);
  if (error) {
    ctx.status = 400;
    ctx.body = { message: error.details[0].message };
    return;
  }

  const { email, password } = value;

  try {
    const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);
    if (user && await bcrypt.compare(password, user.password)) {
      const token = jwt.sign({ username: user.username }, APP_SECRET, { expiresIn: '1h' });
      ctx.status = 200;
      ctx.body = { token, message: 'Login successful' };
    } else {
      ctx.status = 401;
      ctx.body = { message: 'Invalid email or password' };
    }
  } catch (error) {
    ctx.status = 500;
    ctx.body = { message: 'Internal server error' };
  }
});

router.post('/set_secret', async (ctx) => {
  const { error, value } = secretSchema.validate(ctx.request.body);
  if (error) {
    ctx.status = 400;
    ctx.body = { message: error.details[0].message };
    return;
  }

  const { username, secret } = value;
  const authHeader = ctx.headers['authorization'];
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    ctx.status = 401;
    ctx.body = { message: 'Invalid authentication token' };
    return;
  }

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, APP_SECRET);
    if (decoded.username !== username) {
      throw new Error('Invalid token');
    }
    await db.run('INSERT INTO secrets (username, secret) VALUES (?, ?)', [username, secret]);
    ctx.status = 200;
    ctx.body = { message: 'Secret has been set successfully' };
  } catch (error) {
    ctx.status = 401;
    ctx.body = { message: 'Invalid authentication token' };
  }
});

router.get('/get_secret', async (ctx) => {
  const { username } = ctx.query;
  const authHeader = ctx.headers['authorization'];
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    ctx.status = 401;
    ctx.body = { message: 'Invalid authentication token' };
    return;
  }

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, APP_SECRET);
    if (decoded.username !== username) {
      throw new Error('Invalid token');
    }
    const secret = await db.get('SELECT secret FROM secrets WHERE username = ?', [username]);
    if (secret) {
      ctx.status = 200;
      ctx.body = { secret: secret.secret };
    } else {
      ctx.status = 404;
      ctx.body = { message: 'Secret not found' };
    }
  } catch (error) {
    ctx.status = 401;
    ctx.body = { message: 'Invalid authentication token' };
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(PORT, () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});