const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');

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

// Routes
router.post('/invite_user', async (ctx) => {
  const { email } = ctx.request.body;

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    ctx.status = 400;
    ctx.body = { message: 'Invalid email format' };
    return;
  }

  let invite = await db.get('SELECT invite_id FROM invitations WHERE email = ?', [email]);

  if (!invite) {
    const invite_id = uuidv4();
    await db.run('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', [email, invite_id]);
    invite = { invite_id };
  }

  ctx.body = {
    invite_id: invite.invite_id,
    message: 'Invitation created or retrieved successfully'
  };
});

router.post('/create_user', async (ctx) => {
  const { invite_id, user_name, password } = ctx.request.body;

  if (!invite_id || !user_name || !password) {
    ctx.status = 400;
    ctx.body = { message: 'Invite ID, username, and password are required' };
    return;
  }

  if (user_name.length < 3 || user_name.length > 30) {
    ctx.status = 400;
    ctx.body = { message: 'Invalid username length' };
    return;
  }

  if (password.length < 8) {
    ctx.status = 400;
    ctx.body = { message: 'Password must be at least 8 characters long' };
    return;
  }

  const invite = await db.get('SELECT email FROM invitations WHERE invite_id = ?', [invite_id]);

  if (!invite) {
    ctx.status = 401;
    ctx.body = { message: 'Invalid invite_id' };
    return;
  }

  const existingUser = await db.get('SELECT user_name FROM users WHERE user_name = ?', [user_name]);

  if (existingUser) {
    ctx.status = 400;
    ctx.body = { message: 'Username already exists. Try providing different username.' };
    return;
  }

  const hashedPassword = await bcrypt.hash(password, 10);
  await db.run('INSERT INTO users (user_name, password) VALUES (?, ?)', [user_name, hashedPassword]);

  ctx.body = { message: 'User created successfully' };
});

// Apply routes
app.use(router.routes()).use(router.allowedMethods());

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});