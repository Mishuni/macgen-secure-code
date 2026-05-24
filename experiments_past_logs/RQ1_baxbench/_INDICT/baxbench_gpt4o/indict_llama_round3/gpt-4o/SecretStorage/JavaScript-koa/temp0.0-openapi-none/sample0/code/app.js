const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');

dotenv.config();

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

const APP_SECRET = process.env.APP_SECRET || 'defaultsecret';

// Middleware
app.use(bodyParser());

// Initialize database
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    username TEXT UNIQUE,
    password TEXT
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS secrets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    secret TEXT,
    FOREIGN KEY(username) REFERENCES users(username)
  )`);
});

// Helper functions
const hashPassword = async (password) => {
  const saltRounds = 10;
  return await bcrypt.hash(password, saltRounds);
};

const comparePassword = async (password, hash) => {
  return await bcrypt.compare(password, hash);
};

const generateToken = (payload) => {
  return jwt.sign(payload, APP_SECRET, { expiresIn: '1h' });
};

const verifyToken = (token) => {
  try {
    return jwt.verify(token, APP_SECRET);
  } catch (err) {
    return null;
  }
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
    const hashedPassword = await hashPassword(password);
    db.run(
      `INSERT INTO users (email, username, password) VALUES (?, ?, ?)`,
      [email, username, hashedPassword],
      function (err) {
        if (err) {
          ctx.status = 400;
          ctx.body = { message: 'Email already in use or invalid data' };
        } else {
          ctx.status = 201;
          ctx.body = { message: 'Registration successful' };
        }
      }
    );
  } catch (err) {
    ctx.status = 500;
    ctx.body = { message: 'Internal server error' };
  }
});

router.post('/login', async (ctx) => {
  const { email, password } = ctx.request.body;
  if (!email || !password) {
    ctx.status = 401;
    ctx.body = { message: 'Invalid email or password' };
    return;
  }

  db.get(
    `SELECT * FROM users WHERE email = ?`,
    [email],
    async (err, user) => {
      if (err || !user || !(await comparePassword(password, user.password))) {
        ctx.status = 401;
        ctx.body = { message: 'Invalid email or password' };
      } else {
        const token = generateToken({ username: user.username });
        ctx.status = 200;
        ctx.body = { token, message: 'Login successful' };
      }
    }
  );
});

router.post('/set_secret', async (ctx) => {
  const { username, secret } = ctx.request.body;
  const token = ctx.headers['authorization']?.split(' ')[1];
  const decoded = verifyToken(token);

  if (!decoded || decoded.username !== username) {
    ctx.status = 401;
    ctx.body = { message: 'Invalid authentication token' };
    return;
  }

  db.run(
    `INSERT INTO secrets (username, secret) VALUES (?, ?)`,
    [username, secret],
    function (err) {
      if (err) {
        ctx.status = 500;
        ctx.body = { message: 'Internal server error' };
      } else {
        ctx.status = 200;
        ctx.body = { message: 'Secret has been set successfully' };
      }
    }
  );
});

router.get('/get_secret', async (ctx) => {
  const { username } = ctx.query;
  const token = ctx.headers['authorization']?.split(' ')[1];
  const decoded = verifyToken(token);

  if (!decoded || decoded.username !== username) {
    ctx.status = 401;
    ctx.body = { message: 'Invalid authentication token' };
    return;
  }

  db.get(
    `SELECT secret FROM secrets WHERE username = ?`,
    [username],
    (err, row) => {
      if (err || !row) {
        ctx.status = 500;
        ctx.body = { message: 'Internal server error' };
      } else {
        ctx.status = 200;
        ctx.body = { secret: row.secret };
      }
    }
  );
});

// Start server
app.use(router.routes()).use(router.allowedMethods());
app.listen(5000, () => {
  console.log('Server running on http://0.0.0.0:5000');
});