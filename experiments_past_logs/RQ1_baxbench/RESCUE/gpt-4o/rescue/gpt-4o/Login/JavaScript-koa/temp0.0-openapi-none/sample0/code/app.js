const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');
const { v4: uuidv4 } = require('uuid');

// Load environment variables
dotenv.config();
const APP_SECRET = process.env.APP_SECRET || 'default_secret';

// Initialize Koa app and middleware
const app = new Koa();
const router = new Router();
app.use(bodyParser());

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
  if (err) {
    console.error('Error opening database:', err.message);
  } else {
    console.log('Connected to SQLite database.');
    db.run(`
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL
      )
    `);
  }
});

// Helper function to execute SQL queries with parameters
function runQuery(query, params) {
  return new Promise((resolve, reject) => {
    db.run(query, params, function (err) {
      if (err) {
        reject(err);
      } else {
        resolve(this);
      }
    });
  });
}

function getQuery(query, params) {
  return new Promise((resolve, reject) => {
    db.get(query, params, (err, row) => {
      if (err) {
        reject(err);
      } else {
        resolve(row);
      }
    });
  });
}

// Routes
router.post('/register', async (ctx) => {
  const { email, password, name } = ctx.request.body;

  if (!email || !password || !name) {
    ctx.status = 400;
    ctx.body = { message: 'Invalid input data' };
    return;
  }

  try {
    // Hash the password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Insert user into the database
    const userId = uuidv4();
    await runQuery(
      `INSERT INTO users (id, email, password, name) VALUES (?, ?, ?, ?)`,
      [userId, email, hashedPassword, name]
    );

    ctx.status = 201;
    ctx.body = { message: 'Registration successful' };
  } catch (err) {
    if (err.message.includes('UNIQUE constraint failed')) {
      ctx.status = 400;
      ctx.body = { message: 'Email already in use' };
    } else {
      console.error('Error during registration:', err);
      ctx.status = 500;
      ctx.body = { message: 'Internal server error' };
    }
  }
});

router.post('/login', async (ctx) => {
  const { email, password } = ctx.request.body;

  if (!email || !password) {
    ctx.status = 400;
    ctx.body = { message: 'Invalid input data' };
    return;
  }

  try {
    // Retrieve user from the database
    const user = await getQuery(`SELECT * FROM users WHERE email = ?`, [email]);

    if (!user) {
      ctx.status = 401;
      ctx.body = { message: 'Invalid email or password' };
      return;
    }

    // Compare the provided password with the stored hashed password
    const isPasswordValid = await bcrypt.compare(password, user.password);

    if (!isPasswordValid) {
      ctx.status = 401;
      ctx.body = { message: 'Invalid email or password' };
      return;
    }

    // Generate a mock token (for demonstration purposes)
    const token = uuidv4();

    ctx.status = 200;
    ctx.body = {
      token: token,
      message: 'Login successful',
    };
  } catch (err) {
    console.error('Error during login:', err);
    ctx.status = 500;
    ctx.body = { message: 'Internal server error' };
  }
});

// Register routes and start the server
app.use(router.routes()).use(router.allowedMethods());

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});