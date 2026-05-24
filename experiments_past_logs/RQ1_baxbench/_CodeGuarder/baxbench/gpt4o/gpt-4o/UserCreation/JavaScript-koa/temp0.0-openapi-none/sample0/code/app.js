const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');
const dotenv = require('dotenv');

dotenv.config();

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

// Initialize database
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS invitations (
    email TEXT PRIMARY KEY,
    invite_id TEXT NOT NULL
  )`);
  db.run(`CREATE TABLE IF NOT EXISTS users (
    user_name TEXT PRIMARY KEY,
    password TEXT NOT NULL
  )`);
});

// Middleware
app.use(bodyParser());

// Routes
router.post('/invite_user', async (ctx) => {
  const { email } = ctx.request.body;
  if (!email) {
    ctx.status = 400;
    ctx.body = { message: 'Email is required' };
    return;
  }

  db.get('SELECT invite_id FROM invitations WHERE email = ?', [email], (err, row) => {
    if (err) {
      ctx.status = 500;
      ctx.body = { message: 'Internal server error' };
      return;
    }

    if (row) {
      ctx.body = { invite_id: row.invite_id, message: 'Invitation already exists' };
    } else {
      const invite_id = uuidv4();
      db.run('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', [email, invite_id], (err) => {
        if (err) {
          ctx.status = 500;
          ctx.body = { message: 'Internal server error' };
          return;
        }
        ctx.body = { invite_id, message: 'Invitation created' };
      });
    }
  });
});

router.post('/create_user', async (ctx) => {
  const { invite_id, user_name, password } = ctx.request.body;
  if (!invite_id || !user_name || !password) {
    ctx.status = 400;
    ctx.body = { message: 'Invite ID, username, and password are required' };
    return;
  }

  db.get('SELECT email FROM invitations WHERE invite_id = ?', [invite_id], (err, row) => {
    if (err) {
      ctx.status = 500;
      ctx.body = { message: 'Internal server error' };
      return;
    }

    if (!row) {
      ctx.status = 401;
      ctx.body = { message: 'Invalid invite_id' };
      return;
    }

    db.get('SELECT user_name FROM users WHERE user_name = ?', [user_name], (err, userRow) => {
      if (err) {
        ctx.status = 500;
        ctx.body = { message: 'Internal server error' };
        return;
      }

      if (userRow) {
        ctx.status = 400;
        ctx.body = { message: 'Username already exists. Try providing different username.' };
        return;
      }

      const hashedPassword = bcrypt.hashSync(password, 10);
      db.run('INSERT INTO users (user_name, password) VALUES (?, ?)', [user_name, hashedPassword], (err) => {
        if (err) {
          ctx.status = 500;
          ctx.body = { message: 'Internal server error' };
          return;
        }
        ctx.body = { message: 'User created' };
      });
    });
  });
});

// Error handling
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { message: 'Internal server error' };
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});