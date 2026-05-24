const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

const app = new Koa();
const router = new Router();

// Database setup
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database,
  });

  // Create tables if they don't exist
  await db.exec(`
    CREATE TABLE IF NOT EXISTS invitations (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_name TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      invite_id TEXT NOT NULL,
      FOREIGN KEY (invite_id) REFERENCES invitations (id)
    );
  `);
})();

// Middleware
app.use(bodyParser());

// Routes

// POST /invite_user
router.post('/invite_user', async (ctx) => {
  const { email } = ctx.request.body;

  if (!email) {
    ctx.status = 400;
    ctx.body = { message: 'Email is required' };
    return;
  }

  try {
    // Check if an invitation already exists for the email
    const existingInvite = await db.get('SELECT id FROM invitations WHERE email = ?', [email]);

    if (existingInvite) {
      ctx.body = {
        invite_id: existingInvite.id,
        message: 'Invitation already exists for this email',
      };
      return;
    }

    // Create a new invitation
    const inviteId = uuidv4();
    await db.run('INSERT INTO invitations (id, email) VALUES (?, ?)', [inviteId, email]);

    ctx.body = {
      invite_id: inviteId,
      message: 'Invitation created successfully',
    };
  } catch (error) {
    console.error(error);
    ctx.status = 500;
    ctx.body = { message: 'Internal server error' };
  }
});

// POST /create_user
router.post('/create_user', async (ctx) => {
  const { invite_id, user_name, password } = ctx.request.body;

  if (!invite_id || !user_name || !password) {
    ctx.status = 400;
    ctx.body = { message: 'Invite ID, username, and password are required' };
    return;
  }

  try {
    // Check if the invitation exists
    const invitation = await db.get('SELECT id FROM invitations WHERE id = ?', [invite_id]);

    if (!invitation) {
      ctx.status = 401;
      ctx.body = { message: 'Invalid invite_id' };
      return;
    }

    // Check if the username already exists
    const existingUser = await db.get('SELECT id FROM users WHERE user_name = ?', [user_name]);

    if (existingUser) {
      ctx.status = 400;
      ctx.body = { message: 'Username already exists. Try providing a different username.' };
      return;
    }

    // Create the new user
    await db.run(
      'INSERT INTO users (user_name, password, invite_id) VALUES (?, ?, ?)',
      [user_name, password, invite_id]
    );

    ctx.body = { message: 'User created successfully' };
  } catch (error) {
    console.error(error);
    ctx.status = 500;
    ctx.body = { message: 'Internal server error' };
  }
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});