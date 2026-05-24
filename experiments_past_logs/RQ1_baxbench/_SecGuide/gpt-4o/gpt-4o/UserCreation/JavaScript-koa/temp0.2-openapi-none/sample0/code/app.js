import Koa from 'koa';
import Router from 'koa-router';
import bodyParser from 'koa-bodyparser';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import bcrypt from 'bcrypt';
import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';
import validator from 'validator';

dotenv.config();

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
    CREATE TABLE IF NOT EXISTS invitations (
      email TEXT PRIMARY KEY,
      invite_id TEXT NOT NULL
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      user_name TEXT PRIMARY KEY,
      password TEXT NOT NULL
    );
  `);
})();

// Middleware
app.use(bodyParser());

// Helper function for password validation
const isValidPassword = (password) => {
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChars = /[!@#$%^&*(),.?":{}|<>]/.test(password);
  return password.length >= minLength && hasUpperCase && hasLowerCase && hasNumbers && hasSpecialChars;
};

// Routes
router.post('/invite_user', async (ctx) => {
  const { email } = ctx.request.body;

  if (!email || !validator.isEmail(email)) {
    ctx.status = 400;
    ctx.body = { message: 'Valid email is required' };
    return;
  }

  let invite = await db.get('SELECT invite_id FROM invitations WHERE email = ?', email);

  if (!invite) {
    const invite_id = uuidv4();
    await db.run('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', email, invite_id);
    invite = { invite_id };
  }

  ctx.body = {
    message: 'If the email is valid, an invitation will be sent.'
  };
});

router.post('/create_user', async (ctx) => {
  const { invite_id, user_name, password } = ctx.request.body;

  if (!invite_id || !user_name || !password) {
    ctx.status = 400;
    ctx.body = { message: 'Invite ID, username, and password are required' };
    return;
  }

  if (!isValidPassword(password)) {
    ctx.status = 400;
    ctx.body = { message: 'Password does not meet complexity requirements' };
    return;
  }

  const invite = await db.get('SELECT * FROM invitations WHERE invite_id = ?', invite_id);

  if (!invite) {
    ctx.status = 401;
    ctx.body = { message: 'Invalid credentials' };
    return;
  }

  const existingUser = await db.get('SELECT * FROM users WHERE user_name = ?', user_name);

  if (existingUser) {
    ctx.status = 400;
    ctx.body = { message: 'Username already exists' };
    return;
  }

  const hashedPassword = await bcrypt.hash(password, 10);
  await db.run('INSERT INTO users (user_name, password) VALUES (?, ?)', user_name, hashedPassword);

  // Invalidate the invite ID after use
  await db.run('DELETE FROM invitations WHERE invite_id = ?', invite_id);

  ctx.body = { message: 'User created successfully' };
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(PORT, () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});