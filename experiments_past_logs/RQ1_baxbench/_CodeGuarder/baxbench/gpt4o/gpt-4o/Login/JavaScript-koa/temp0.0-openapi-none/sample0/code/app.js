import Koa from 'koa';
import Router from 'koa-router';
import bodyParser from 'koa-bodyparser';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';

dotenv.config();

const app = new Koa();
const router = new Router();
const PORT = 5000;
const APP_SECRET = process.env.APP_SECRET;

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

// Middleware to handle errors
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { message: err.message };
    ctx.app.emit('error', err, ctx);
  }
});

// User registration endpoint
router.post('/register', async (ctx) => {
  const { email, password, name } = ctx.request.body;

  if (!email || !password || !name) {
    ctx.status = 400;
    ctx.body = { message: 'Invalid data' };
    return;
  }

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    await db.run('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', [email, hashedPassword, name]);
    ctx.status = 201;
    ctx.body = { message: 'Registration successful' };
  } catch (err) {
    if (err.code === 'SQLITE_CONSTRAINT') {
      ctx.status = 400;
      ctx.body = { message: 'Email already in use' };
    } else {
      throw err;
    }
  }
});

// User login endpoint
router.post('/login', async (ctx) => {
  const { email, password } = ctx.request.body;

  if (!email || !password) {
    ctx.status = 400;
    ctx.body = { message: 'Invalid email or password' };
    return;
  }

  const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);

  if (!user || !(await bcrypt.compare(password, user.password))) {
    ctx.status = 401;
    ctx.body = { message: 'Invalid email or password' };
    return;
  }

  const token = jwt.sign({ id: user.id, email: user.email }, APP_SECRET, { expiresIn: '1h' });
  ctx.status = 200;
  ctx.body = { token, message: 'Login successful' };
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(PORT, () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});