const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');
const { v4: uuidv4 } = require('uuid');

dotenv.config();

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

// Middleware to parse JSON bodies
app.use(bodyParser());

// Initialize the database
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS USERS (
    ID TEXT PRIMARY KEY,
    EMAIL TEXT UNIQUE NOT NULL,
    PASSWORD TEXT NOT NULL,
    NAME TEXT NOT NULL
  )`);
});

// User registration endpoint
router.post('/register', async (ctx) => {
  const { email, password, name } = ctx.request.body;

  if (!email || !password || !name) {
    ctx.status = 400;
    ctx.body = { message: 'Email, password, and name are required.' };
    return;
  }

  const hashedPassword = await bcrypt.hash(password, 10);
  const id = uuidv4();

  db.run(`INSERT INTO USERS (ID, EMAIL, PASSWORD, NAME) VALUES (?, ?, ?, ?)`, [id, email, hashedPassword, name], function(err) {
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

  db.get(`SELECT PASSWORD FROM USERS WHERE EMAIL = ?`, [email], async (err, row) => {
    if (err || !row) {
      ctx.status = 401;
      ctx.body = { message: 'Invalid email or password' };
      return;
    }

    const isPasswordValid = await bcrypt.compare(password, row.PASSWORD);
    if (!isPasswordValid) {
      ctx.status = 401;
      ctx.body = { message: 'Invalid email or password' };
      return;
    }

    ctx.status = 200;
    ctx.body = { token: 'jwt-token-abc123', message: 'Login successful' }; // Placeholder token
  });
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
  console.log('Server is running on http://0.0.0.0:5000');
});