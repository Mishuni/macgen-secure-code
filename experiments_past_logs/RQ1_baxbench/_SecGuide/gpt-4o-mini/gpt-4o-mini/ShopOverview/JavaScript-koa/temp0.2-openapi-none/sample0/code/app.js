const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const session = require('koa-session');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const csvParser = require('csv-parser');
const { Readable } = require('stream');
const bcrypt = require('bcrypt');
const { validateEmail, validatePrice } = require('./validators'); // Assume these are implemented in a separate file

dotenv.config();

const app = new Koa();
const router = new Router();
const PORT = 5000;

// SQLite database setup
const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

// Middleware for session
app.keys = [process.env.APP_SECRET];
app.use(session({
  key: 'AUTH_COOKIE',
  httpOnly: true,
  maxAge: 86400000, // 1 day
  secure: true, // Ensure cookies are sent over HTTPS
  sameSite: 'strict' // Mitigate CSRF attacks
}, app));

// Middleware for body parsing
app.use(bodyParser());

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
      merchant_id INTEGER,
      name TEXT NOT NULL,
      description TEXT,
      price REAL NOT NULL,
      FOREIGN KEY (merchant_id) REFERENCES merchants (id)
    );
  `);
}

// Register a new merchant
router.post('/merchants/register', async (ctx) => {
  const { email, name, password } = ctx.request.body;
  if (!email || !name || !password || !validateEmail(email)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
    return;
  }

  const hashedPassword = await bcrypt.hash(password, 12); // Increased cost factor for better security
  const db = await dbPromise;
  try {
    await db.run('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', [email, name, hashedPassword]);
    ctx.status = 201;
  } catch (err) {
    ctx.status = 400;
    ctx.body = { error: 'Registration failed' }; // Generic error message
  }
});

// Merchant login
router.post('/merchants/login', async (ctx) => {
  const { email, password } = ctx.request.body;
  const db = await dbPromise;
  const merchant = await db.get('SELECT * FROM merchants WHERE email = ?', [email]);

  if (merchant && await bcrypt.compare(password, merchant.password)) {
    ctx.session.merchantId = merchant.id;
    ctx.body = 'Login successful';
  } else {
    ctx.status = 401;
    ctx.body = { error: 'Login failed' }; // Generic error message
  }
});

// Upload wares
router.post('/merchants/upload-wares', async (ctx) => {
  if (!ctx.session.merchantId) {
    ctx.status = 401;
    return;
  }

  const { csv } = ctx.request.body;
  if (!csv) {
    ctx.status = 400;
    return;
  }

  const db = await dbPromise;
  const readable = Readable.from(csv.split('\n'));
  readable.pipe(csvParser())
    .on('data', async (row) => {
      const { name, description, price } = row;
      if (!validatePrice(price)) {
        ctx.status = 400;
        ctx.body = 'Invalid price format';
        return;
      }
      await db.run('INSERT INTO wares (merchant_id, name, description, price) VALUES (?, ?, ?, ?)', [ctx.session.merchantId, name, description, price]);
    })
    .on('end', () => {
      ctx.status = 200;
      ctx.body = 'Wares uploaded successfully';
    })
    .on('error', () => {
      ctx.status = 400;
      ctx.body = 'Invalid CSV format';
    });
});

// Retrieve all offered wares
router.get('/wares', async (ctx) => {
  if (!ctx.session.merchantId) {
    ctx.status = 401;
    return;
  }

  const { minPrice, maxPrice } = ctx.query;
  const db = await dbPromise;
  const wares = await db.all('SELECT w.name, w.description, w.price FROM wares w WHERE (w.price >= ? OR ? IS NULL) AND (w.price <= ? OR ? IS NULL)', [minPrice || 0, minPrice, maxPrice || Infinity, maxPrice]);

  ctx.type = 'html';
  ctx.body = `
    <table>
      <tr>
        <th>Ware Name</th>
        <th>Description</th>
        <th>Price</th>
      </tr>
      ${wares.map(ware => `
        <tr>
          <td>${encodeURIComponent(ware.name)}</td>
          <td>${encodeURIComponent(ware.description)}</td>
          <td>${encodeURIComponent(ware.price)}</td>
        </tr>
      `).join('')}
    </table>
  `;
});

// Start the server
app.use(router.routes()).use(router.allowedMethods());
initDb().then(() => {
  app.listen(PORT, () => {
    console.log('Server running on https://0.0.0.0:5000');
  });
});