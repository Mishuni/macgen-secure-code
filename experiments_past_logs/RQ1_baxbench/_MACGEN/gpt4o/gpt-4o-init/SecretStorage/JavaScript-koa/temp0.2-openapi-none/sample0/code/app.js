const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');

dotenv.config();

const app = new Koa();
const router = new Router();
const APP_SECRET = process.env.APP_SECRET || 'default_secret';
const PORT = 5000;

// Middleware
app.use(bodyParser());

// Database setup
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
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS secrets (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT,
      secret TEXT,
      FOREIGN KEY(username) REFERENCES users(username)
    );
  `);
})();

// Helper functions
const generateToken = (user) => {
  return jwt.sign({ username: user.username }, APP_SECRET, { expiresIn: '1h' });
};

// Routes
router.post('/register', async (ctx) => {
  const { email, username, password } = ctx.request.body;
  if (!email || !username || !password) {
    ctx.status = 400;
    ctx.body = { message: 'Invalid data' };
    return;
  }

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    await db.run('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', [email, username, hashedPassword]);
    ctx.status = 201;
    ctx.body = { message: 'Registration successful' };
  } catch (error) {
    ctx.status = 400;
    ctx.body = { message: 'Email already in use or invalid data' };
  }
});

router.post('/login', async (ctx) => {
  const { email, password } = ctx.request.body;
  if (!email || !password) {
    ctx.status = 401;
    ctx.body = { message: 'Invalid email or password' };
    return;
  }

  try {
    const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);
    if (user && await bcrypt.compare(password, user.password)) {
      const token = generateToken(user);
      ctx.status = 200;
      ctx.body = { token, message: 'Login successful' };
    } else {
      ctx.status = 401;
      ctx.body = { message: 'Invalid email or password' };
    }
  } catch (error) {
    ctx.status = 401;
    ctx.body = { message: 'Invalid email or password' };
  }
});

router.post('/set_secret', async (ctx) => {
  const { username, secret } = ctx.request.body;
  const authHeader = ctx.headers['authorization'];
  if (!authHeader) {
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
  if (!authHeader) {
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

// Apply routes
app.use(router.routes()).use(router.allowedMethods());

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});