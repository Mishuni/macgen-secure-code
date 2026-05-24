
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
    password TEXT,
    name TEXT
  )`);
});

// Helper functions
const hashPassword = async (password) => {
  const saltRounds = 10;
  return await bcrypt.hash(password, saltRounds);
};

const verifyPassword = async (password, hash) => {
  return await bcrypt.compare(password, hash);
};

const generateToken = (email) => {
  return jwt.sign({ email }, APP_SECRET, { expiresIn: '1h' });
};

// Routes
router.post('/register', async (ctx) => {
  const { email, password, name } = ctx.request.body;
  if (!email || !password || !name) {
    ctx.status = 400;
    ctx.body = { message: 'Invalid data' };
    return;
  }

  try {
    const hashedPassword = await hashPassword(password);
    db.run(`INSERT INTO users (email, password, name) VALUES (?, ?, ?)`, [email, hashedPassword, name], function (err) {
      if (err) {
        ctx.status = 400;
        ctx.body = { message: 'Email already in use or invalid data' };
      } else {
        ctx.status = 201;
        ctx.body = { message: 'Registration successful' };
      }
    });
  } catch (error) {
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

  db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, user) => {
    if (err || !user) {
      ctx.status = 401;
      ctx.body = { message: 'Invalid email or password' };
    } else {
      const isPasswordValid = await verifyPassword(password, user.password);
      if (isPasswordValid) {
        const token = generateToken(email);
        ctx.status = 200;
        ctx.body = { token, message: 'Login successful' };
      } else {
        ctx.status = 401;
        ctx.body = { message: 'Invalid email or password' };
      }
    }
  });
});

// Apply routes
app.use(router.routes()).use(router.allowedMethods());

// Start server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});