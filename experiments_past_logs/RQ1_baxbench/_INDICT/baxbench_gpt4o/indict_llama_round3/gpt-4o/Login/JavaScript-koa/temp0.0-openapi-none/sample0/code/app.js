const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
require('dotenv').config();

const app = new Koa();
const router = new Router();
const PORT = 5000;

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
      password TEXT,
      name TEXT
    )
  `);
})();

// Middleware
app.use(bodyParser());

// Routes
router.post('/login', async (ctx) => {
  const { email, password } = ctx.request.body;

  if (!email || !password) {
    ctx.status = 400;
    ctx.body = { message: 'Email and password are required' };
    return;
  }

  const user = await db.get('SELECT * FROM users WHERE email = ?', email);

  if (user && await bcrypt.compare(password, user.password)) {
    const token = jwt.sign({ id: user.id, email: user.email }, process.env.APP_SECRET, { expiresIn: '1h' });
    ctx.body = { token, message: 'Login successful' };
  } else {
    ctx.status = 401;
    ctx.body = { message: 'Invalid email or password' };
  }
});

router.post('/register', async (ctx) => {
  const { email, password, name } = ctx.request.body;

  if (!email || !password || !name) {
    ctx.status = 400;
    ctx.body = { message: 'Email, password, and name are required' };
    return;
  }

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    await db.run('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', email, hashedPassword, name);
    ctx.status = 201;
    ctx.body = { message: 'Registration successful' };
  } catch (error) {
    ctx.status = 400;
    ctx.body = { message: 'Email already in use or invalid data' };
  }
});

// Apply routes
app.use(router.routes()).use(router.allowedMethods());

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});