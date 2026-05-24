const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');
const fs = require('fs');
const path = require('path');

// Load environment variables
dotenv.config();

const app = new Koa();
const router = new Router();
const APP_SECRET = process.env.APP_SECRET || 'default_secret';
const PORT = 5000;

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database,
  });

  // Create tables if they don't exist
  await db.exec(`
    CREATE TABLE IF NOT EXISTS merchants (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      name TEXT NOT NULL,
      password TEXT NOT NULL
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS wares (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      description TEXT NOT NULL,
      price REAL NOT NULL,
      merchant_id INTEGER NOT NULL,
      FOREIGN KEY (merchant_id) REFERENCES merchants(id)
    );
  `);
})();

// Middleware
app.use(bodyParser());

// Helper function to validate email
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Routes
router.post('/merchants/register', async (ctx) => {
  const { email, name, password } = ctx.request.body;

  if (!email || !name || !password || !isValidEmail(email)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
    return;
  }

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    await db.run(
      'INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)',
      [email, name, hashedPassword]
    );
    ctx.status = 201;
    ctx.body = { message: 'Merchant registered successfully' };
  } catch (err) {
    if (err.code === 'SQLITE_CONSTRAINT') {
      ctx.status = 400;
      ctx.body = { error: 'Email already exists' };
    } else {
      ctx.status = 500;
      ctx.body = { error: 'Internal server error' };
    }
  }
});

router.post('/merchants/login', async (ctx) => {
  const { email, password } = ctx.request.body;

  if (!email || !password || !isValidEmail(email)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
    return;
  }

  try {
    const merchant = await db.get(
      'SELECT * FROM merchants WHERE email = ?',
      [email]
    );

    if (merchant && (await bcrypt.compare(password, merchant.password))) {
      ctx.cookies.set('AUTH_COOKIE', merchant.id, {
        httpOnly: true,
        secure: false, // Set to true in production with HTTPS
        sameSite: 'strict',
      });
      ctx.status = 200;
      ctx.body = 'Login successful';
    } else {
      ctx.status = 401;
      ctx.body = { error: 'Invalid email or password' };
    }
  } catch (err) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

router.post('/merchants/upload-wares', async (ctx) => {
  const merchantId = ctx.cookies.get('AUTH_COOKIE');

  if (!merchantId) {
    ctx.status = 401;
    ctx.body = { error: 'Unauthorized' };
    return;
  }

  const { csv } = ctx.request.body;

  if (!csv) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
    return;
  }

  try {
    const rows = csv.split('\n').map((line) => line.split(','));
    const insertPromises = rows.map(([name, description, price]) => {
      if (!name || !description || isNaN(parseFloat(price))) {
        throw new Error('Invalid CSV format');
      }
      return db.run(
        'INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)',
        [name.trim(), description.trim(), parseFloat(price), merchantId]
      );
    });

    await Promise.all(insertPromises);
    ctx.status = 200;
    ctx.body = { message: 'Wares uploaded successfully' };
  } catch (err) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid CSV format' };
  }
});

router.get('/wares', async (ctx) => {
  const merchantId = ctx.cookies.get('AUTH_COOKIE');

  if (!merchantId) {
    ctx.status = 401;
    ctx.body = { error: 'Unauthorized' };
    return;
  }

  const { minPrice, maxPrice } = ctx.query;

  try {
    let query = `
      SELECT wares.name, wares.description, wares.price, merchants.email
      FROM wares
      INNER JOIN merchants ON wares.merchant_id = merchants.id
      WHERE 1=1
    `;
    const params = [];

    if (minPrice) {
      query += ' AND wares.price >= ?';
      params.push(parseFloat(minPrice));
    }

    if (maxPrice) {
      query += ' AND wares.price <= ?';
      params.push(parseFloat(maxPrice));
    }

    const wares = await db.all(query, params);

    const html = `
      <table border="1">
        <tr>
          <th>Name</th>
          <th>Description</th>
          <th>Price</th>
          <th>Merchant Email</th>
        </tr>
        ${wares
          .map(
            (ware) => `
          <tr>
            <td>${ware.name}</td>
            <td>${ware.description}</td>
            <td>${ware.price}</td>
            <td>${ware.email}</td>
          </tr>
        `
          )
          .join('')}
      </table>
    `;

    ctx.status = 200;
    ctx.type = 'html';
    ctx.body = html;
  } catch (err) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});