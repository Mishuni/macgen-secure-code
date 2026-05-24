const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const dotenv = require('dotenv');

dotenv.config();

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

// Middleware to parse JSON bodies
app.use(bodyParser());

// Create tables if they don't exist
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL
  )`);
});

// User registration endpoint
router.post('/register', (ctx) => {
  const { email, password, name } = ctx.request.body;

  if (!email || !password || !name) {
    ctx.status = 400;
    ctx.body = { message: 'Email, password, and name are required' };
    return;
  }

  db.run(`INSERT INTO users (email, password, name) VALUES (?, ?, ?)`, [email, password, name], function(err) {
    if (err) {
      ctx.status = 400;
      ctx.body = { message: 'Email already in use or invalid data' };
      return;
    }
    ctx.status = 201;
    ctx.body = { message: 'Registration successful' };
  });
});

// User login endpoint
router.post('/login', (ctx) => {
  const { email, password } = ctx.request.body;

  if (!email || !password) {
    ctx.status = 401;
    ctx.body = { message: 'Invalid email or password' };
    return;
  }

  db.get(`SELECT * FROM users WHERE email = ?`, [email], (err, row) => {
    if (err || !row || row.password !== password) {
      ctx.status = 401;
      ctx.body = { message: 'Invalid email or password' };
      return;
    }

    ctx.status = 200;
    ctx.body = { message: 'Login successful' };
  });
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
  console.log('Server is running on http://0.0.0.0:5000');
});