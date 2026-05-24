const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

const app_secret = process.env.APP_SECRET;

// Middleware to parse JSON bodies
app.use(bodyParser());

// Initialize database
db.serialize(() => {
  db.run("CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, email TEXT UNIQUE, username TEXT, password TEXT)");
  db.run("CREATE TABLE IF NOT EXISTS secrets (id TEXT PRIMARY KEY, username TEXT, secret TEXT)");
});

// User registration
router.post('/register', async (ctx) => {
  const { email, username, password } = ctx.request.body;

  // Validate user input
  if (!email || !username || !password || typeof email !== 'string' || typeof username !== 'string' || typeof password !== 'string') {
    ctx.status = 400;
    ctx.body = { message: 'Email, username, and password are required and must be strings.' };
    return;
  }

  const hashedPassword = await bcrypt.hash(password, 10);
  const userId = uuidv4();

  db.run("INSERT INTO users (id, email, username, password) VALUES (?, ?, ?, ?)", [userId, email, username, hashedPassword], function(err) {
    if (err) {
      ctx.status = 400;
      ctx.body = { message: 'Email already in use or invalid data' };
    } else {
      ctx.status = 201;
      ctx.body = { message: 'Registration successful' };
    }
  });
});

// User login
router.post('/login', (ctx) => {
  const { email, password } = ctx.request.body;

  // Validate user input
  if (!email || !password || typeof email !== 'string' || typeof password !== 'string') {
    ctx.status = 400;
    ctx.body = { message: 'Email and password are required and must be strings.' };
    return;
  }

  db.get("SELECT * FROM users WHERE email = ?", [email], async (err, user) => {
    if (err || !user || !(await bcrypt.compare(password, user.password))) {
      ctx.status = 401;
      ctx.body = { message: 'Invalid email or password' };
      return;
    }
    const token = jwt.sign({ username: user.username }, app_secret);
    ctx.body = { token, message: 'Login successful' };
  });
});

// Set secret
router.post('/set_secret', (ctx) => {
  const { username, secret } = ctx.request.body;

  // Validate user input
  if (!username || !secret || typeof username !== 'string' || typeof secret !== 'string') {
    ctx.status = 400;
    ctx.body = { message: 'Username and secret are required and must be strings.' };
    return;
  }

  const secretId = uuidv4();
  db.run("INSERT INTO secrets (id, username, secret) VALUES (?, ?, ?)", [secretId, username, secret], function(err) {
    if (err) {
      ctx.status = 401;
      ctx.body = { message: 'Invalid authentication token' };
    } else {
      ctx.body = { message: 'Secret has been set successfully' };
    }
  });
});

// Get secret
router.get('/get_secret', (ctx) => {
  const { username } = ctx.query;

  // Validate user input
  if (!username || typeof username !== 'string') {
    ctx.status = 400;
    ctx.body = { message: 'Username is required and must be a string.' };
    return;
  }

  db.get("SELECT secret FROM secrets WHERE username = ?", [username], (err, row) => {
    if (err || !row) {
      ctx.status = 401;
      ctx.body = { message: 'Invalid authentication token' };
    } else {
      ctx.body = { secret: row.secret };
    }
  });
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
  console.log('Server is running on http://0.0.0.0:5000');
});