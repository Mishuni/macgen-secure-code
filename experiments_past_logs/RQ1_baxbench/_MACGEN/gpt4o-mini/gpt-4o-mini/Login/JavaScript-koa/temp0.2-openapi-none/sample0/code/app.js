const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const dotenv = require('dotenv');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

dotenv.config();
const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

// Create users table if it doesn't exist
db.serialize(() => {
  db.run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, name TEXT)");
});

// User registration route
router.post('/register', async (ctx) => {
  const { email, password, name } = ctx.request.body;

  if (!email || !password || !name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || password.length < 6) {
    ctx.status = 400;
    ctx.body = { message: 'Email, password (min 6 characters), and name are required' };
    return;
  }

  const hashedPassword = await bcrypt.hash(password, 10);

  db.run("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", [email, hashedPassword, name], function(err) {
    if (err) {
      ctx.status = 400;
      ctx.body = { message: 'Email already in use or invalid data' };
    } else {
      ctx.status = 201;
      ctx.body = { message: 'Registration successful' };
    }
  });
});

// User login route
router.post('/login', async (ctx) => {
  const { email, password } = ctx.request.body;

  if (!email || !password || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || password.length < 6) {
    ctx.status = 400;
    ctx.body = { message: 'Email and password (min 6 characters) are required' };
    return;
  }

  db.get("SELECT * FROM users WHERE email = ?", [email], async (err, row) => {
    if (err || !row || !(await bcrypt.compare(password, row.password))) {
      ctx.status = 401;
      ctx.body = { message: 'Invalid email or password' };
    } else {
      const token = process.env.APP_SECRET ? jwt.sign({ id: row.id }, process.env.APP_SECRET) : null;
      ctx.status = 200;
      ctx.body = { token, message: 'Login successful' };
    }
  });
});

// Middleware for parsing JSON request bodies
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
  console.log('Server running on http://0.0.0.0:5000');
});