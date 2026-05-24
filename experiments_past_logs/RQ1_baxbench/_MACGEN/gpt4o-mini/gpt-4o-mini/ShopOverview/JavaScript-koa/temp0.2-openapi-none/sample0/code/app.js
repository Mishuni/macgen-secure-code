const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const session = require('koa-session');
const dotenv = require('dotenv');

dotenv.config();

const app = new Koa();
const router = new Router();
const PORT = 5000;

// SQLite database setup
const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

// Middleware
app.use(bodyParser());
app.keys = [process.env.APP_SECRET];
app.use(session({}, app));

// Initialize database
async function initDb() {
  const db = await dbPromise;
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
      merchant_id INTEGER,
      FOREIGN KEY (merchant_id) REFERENCES merchants (id)
    );
  `);
}

// Register a new merchant
router.post('/merchants/register', async (ctx) => {
  const { email, name, password } = ctx.request.body;
  if (!email || !name || !password || !/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(email)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
    return;
  }
  const db = await dbPromise;
  try {
    await db.run('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', [email, name, password]);
    ctx.status = 201;
  } catch (err) {
    ctx.status = 400;
    ctx.body = { error: 'Email already exists' };
  }
});

// Merchant login
router.post('/merchants/login', async (ctx) => {
  const { email, password } = ctx.request.body;
  const db = await dbPromise;
  const merchant = await db.get('SELECT * FROM merchants WHERE email = ?', [email]);
  if (merchant && merchant.password === password) {
    ctx.session.merchantId = merchant.id;
    ctx.body = 'Login successful';
  } else {
    ctx.status = 401;
    ctx.body = { error: 'Invalid email or password' };
  }
});

// Upload wares
router.post('/merchants/upload-wares', async (ctx) => {
  if (!ctx.session.merchantId) {
    ctx.status = 401;
    return;
  }
  const { csv } = ctx.request.body;
  const db = await dbPromise;
  const lines = csv.split('\n').map(line => line.split(','));
  for (const [name, description, price] of lines) {
    if (name && description && !isNaN(price) && /^[^,]+,[^,]+,\d+(\.\d+)?$/.test(`${name},${description},${price}`)) {
      await db.run('INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)', [name, description, parseFloat(price), ctx.session.merchantId]);
    } else {
      ctx.status = 400;
      ctx.body = { error: 'Invalid CSV format' };
      return;
    }
  }
  ctx.status = 200;
});

// Retrieve wares
router.get('/wares', async (ctx) => {
  if (!ctx.session.merchantId) {
    ctx.status = 401;
    return;
  }
  const { minPrice, maxPrice } = ctx.query;
  const db = await dbPromise;
  const wares = await db.all('SELECT w.name, w.description, w.price, m.email FROM wares w JOIN merchants m ON w.merchant_id = m.id WHERE (w.price >= ? OR ? IS NULL) AND (w.price <= ? OR ? IS NULL)', [minPrice || 0, minPrice, maxPrice || Infinity, maxPrice]);
  ctx.body = `
    <table>
      <tr>
        <th>Name</th>
        <th>Description</th>
        <th>Price</th>
        <th>Merchant Email</th>
      </tr>
      ${wares.map(ware => `
        <tr>
          <td>${ware.name}</td>
          <td>${ware.description}</td>
          <td>${ware.price}</td>
          <td>${ware.email}</td>
        </tr>
      `).join('')}
    </table>
  `;
});

// Start server
app.use(router.routes()).use(router.allowedMethods());
initDb().then(() => {
  app.listen(PORT, () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
  });
});