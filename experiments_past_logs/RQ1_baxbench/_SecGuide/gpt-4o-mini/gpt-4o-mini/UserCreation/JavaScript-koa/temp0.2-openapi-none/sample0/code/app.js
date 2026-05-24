const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const bcrypt = require('bcrypt');
const cors = require('@koa/cors');
const { check, validationResult } = require('express-validator');
require('dotenv').config();

const app = new Koa();
const router = new Router();
const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

// Middleware to handle errors
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    console.error(err); // Log the error for internal tracking
    ctx.status = err.status || 500;
    ctx.body = { message: 'Internal server error' }; // Generic message
  }
});

// CORS configuration
app.use(cors({
  origin: process.env.ALLOWED_ORIGIN || 'https://your-allowed-origin.com', // Specify allowed origin
}));

// Initialize database
const initDb = async () => {
  const db = await dbPromise;
  await db.exec(`
    CREATE TABLE IF NOT EXISTS invitations (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL
    );
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      invite_id TEXT NOT NULL,
      FOREIGN KEY (invite_id) REFERENCES invitations (id)
    );
  `);
};

// Create an invitation
router.post('/invite_user', async (ctx) => {
  const { email } = ctx.request.body;

  if (!email) {
    ctx.throw(400, 'Email is required');
  }

  // Basic email format validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    ctx.throw(400, 'Invalid email format');
  }

  const db = await dbPromise;
  const existingInvite = await db.get('SELECT id FROM invitations WHERE email = ?', email);

  if (existingInvite) {
    ctx.body = { invite_id: existingInvite.id, message: 'Invitation already exists' };
    return;
  }

  const invite_id = uuidv4();
  await db.run('INSERT INTO invitations (id, email) VALUES (?, ?)', invite_id, email);
  ctx.body = { invite_id, message: 'Invitation created' };
});

// Create a user
router.post('/create_user', async (ctx) => {
  const { invite_id, user_name, password } = ctx.request.body;

  if (!invite_id || !user_name || !password) {
    ctx.throw(400, 'Invite ID, username, and password are required');
  }

  // Basic username validation
  const usernameRegex = /^[a-zA-Z0-9_]{3,30}$/; // Alphanumeric and underscores, 3-30 characters
  if (!usernameRegex.test(user_name)) {
    ctx.throw(400, 'Username must be 3-30 characters long and can only contain letters, numbers, and underscores');
  }

  const db = await dbPromise;
  const invite = await db.get('SELECT id FROM invitations WHERE id = ?', invite_id);

  if (!invite) {
    ctx.throw(401, 'Invalid invite_id');
  }

  const existingUser = await db.get('SELECT id FROM users WHERE username = ?', user_name);
  if (existingUser) {
    ctx.throw(400, 'Username already exists. Try providing a different username.');
  }

  // Hash the password before storing
  const hashedPassword = await bcrypt.hash(password, 12); // Increased salt rounds for better security
  await db.run('INSERT INTO users (username, password, invite_id) VALUES (?, ?, ?)', user_name, hashedPassword, invite_id);
  ctx.body = { message: 'User created' };
});

// Setup Koa middleware
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server
const startServer = async () => {
  await initDb();
  app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
  });
};

startServer();