const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const { v4: uuidv4 } = require('uuid');

dotenv.config();

const app = new Koa();
const router = new Router();
const APP_SECRET = process.env.APP_SECRET || 'default_secret';

// Initialize SQLite database
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
    CREATE TABLE IF NOT EXISTS secrets (
      id TEXT PRIMARY KEY,
      user_id TEXT,
      secret TEXT,
      FOREIGN KEY(user_id) REFERENCES users(id)
    );
  `);
})();

// Middleware to handle errors
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { message: err.message };
  }
});

// User registration
router.post('/register', async (ctx) => {
  const { email, username, password } = ctx.request.body;
  if (!email || !username || !password) {
    ctx.status = 400;
    ctx.body = { message: 'Invalid data' };
    return;
  }

  const hashedPassword = await bcrypt.hash(password, 10);
  const userId = uuidv4();

  try {
    await db.run('INSERT INTO users (id, email, username, password) VALUES (?, ?, ?, ?)', [userId, email, username, hashedPassword]);
    ctx.status = 201;
    ctx.body = { message: 'Registration successful' };
  } catch (err) {
    ctx.status = 400;
    ctx.body = { message: 'Email or username already in use' };
  }
});

// User login
router.post('/login', async (ctx) => {
  const { email, password } = ctx.request.body;
  if (!email || !password) {
    ctx.status = 400;
    ctx.body = { message: 'Invalid data' };
    return;
  }

  const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);
  if (user && await bcrypt.compare(password, user.password)) {
    const token = jwt.sign({ id: user.id, username: user.username }, APP_SECRET, { expiresIn: '1h' });
    ctx.body = { token, message: 'Login successful' };
  } else {
    ctx.status = 401;
    ctx.body = { message: 'Invalid email or password' };
  }
});

// Middleware to verify JWT
const authenticate = async (ctx, next) => {
  const authHeader = ctx.headers['authorization'];
  if (!authHeader) {
    ctx.status = 401;
    ctx.body = { message: 'Invalid authentication token' };
    return;
  }

  const token = authHeader.split(' ')[1];
  try {
    const user = jwt.verify(token, APP_SECRET);
    ctx.state.user = user;
    await next();
  } catch (err) {
    ctx.status = 401;
    ctx.body = { message: 'Invalid authentication token' };
  }
};

// Set secret
router.post('/set_secret', authenticate, async (ctx) => {
  const { username, secret } = ctx.request.body;
  if (!username || !secret) {
    ctx.status = 400;
    ctx.body = { message: 'Invalid data' };
    return;
  }

  const user = await db.get('SELECT * FROM users WHERE username = ?', [username]);
  if (user && user.id === ctx.state.user.id) {
    const secretId = uuidv4();
    await db.run('INSERT INTO secrets (id, user_id, secret) VALUES (?, ?, ?)', [secretId, user.id, secret]);
    ctx.body = { message: 'Secret has been set successfully' };
  } else {
    ctx.status = 401;
    ctx.body = { message: 'Unauthorized' };
  }
});

// Get secret
router.get('/get_secret', authenticate, async (ctx) => {
  const { username } = ctx.query;
  if (!username) {
    ctx.status = 400;
    ctx.body = { message: 'Invalid data' };
    return;
  }

  const user = await db.get('SELECT * FROM users WHERE username = ?', [username]);
  if (user && user.id === ctx.state.user.id) {
    const secret = await db.get('SELECT secret FROM secrets WHERE user_id = ?', [user.id]);
    if (secret) {
      ctx.body = { secret: secret.secret };
    } else {
      ctx.status = 404;
      ctx.body = { message: 'Secret not found' };
    }
  } else {
    ctx.status = 401;
    ctx.body = { message: 'Unauthorized' };
  }
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
  console.log('Server running on http://0.0.0.0:5000');
});