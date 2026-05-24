const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const bcrypt = require('bcrypt');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const csvParser = require('csv-parser');
const { Readable } = require('stream');
const jwt = require('jsonwebtoken');

dotenv.config();

const app = new Koa();
const router = new Router();
const APP_SECRET = process.env.APP_SECRET || 'default_secret';
const PORT = 5000;

// Middleware
app.use(bodyParser());

// Database setup
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS merchants (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE,
      name TEXT,
      password TEXT
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS wares (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      merchant_id INTEGER,
      name TEXT,
      description TEXT,
      price REAL,
      FOREIGN KEY (merchant_id) REFERENCES merchants(id)
    );
  `);
})();

// Helper functions
const authenticate = async (ctx, next) => {
  const token = ctx.cookies.get('AUTH_COOKIE');
  if (!token) {
    ctx.status = 401;
    ctx.body = { error: 'Unauthorized' };
    return;
  }
  try {
    const decoded = jwt.verify(token, APP_SECRET);
    ctx.state.merchantId = decoded.id;
    await next();
  } catch (err) {
    ctx.status = 401;
    ctx.body = { error: 'Unauthorized' };
  }
};

// Routes
router.post('/merchants/register', async (ctx) => {
  const { email, name, password } = ctx.request.body;
  if (!email || !name || !password) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }
  const hashedPassword = await bcrypt.hash(password, 10);
  try {
    await db.run('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', [email, name, hashedPassword]);
    ctx.status = 201;
    ctx.body = 'Merchant registered successfully';
  } catch (err) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
  }
});

router.post('/merchants/login', async (ctx) => {
  const { email, password } = ctx.request.body;
  if (!email || !password) {
    ctx.status = 401;
    ctx.body = { error: 'Invalid email or password' };
    return;
  }
  const merchant = await db.get('SELECT * FROM merchants WHERE email = ?', [email]);
  if (merchant && await bcrypt.compare(password, merchant.password)) {
    const token = jwt.sign({ id: merchant.id }, APP_SECRET);
    ctx.cookies.set('AUTH_COOKIE', token, { httpOnly: true, sameSite: 'Lax' });
    ctx.status = 200;
    ctx.body = 'Login successful';
  } else {
    ctx.status = 401;
    ctx.body = { error: 'Invalid email or password' };
  }
});

router.post('/merchants/upload-wares', authenticate, async (ctx) => {
  const { csv } = ctx.request.body;
  if (!csv) {
    ctx.status = 400;
    ctx.body = 'Invalid CSV format';
    return;
  }
  const wares = [];
  const stream = Readable.from([csv]);
  stream.pipe(csvParser())
    .on('data', (row) => {
      if (row.name && row.description && row.price) {
        wares.push({
          name: row.name,
          description: row.description,
          price: parseFloat(row.price),
          merchant_id: ctx.state.merchantId
        });
      }
    })
    .on('end', async () => {
      try {
        const insert = db.prepare('INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)');
        for (const ware of wares) {
          await insert.run(ware.name, ware.description, ware.price, ware.merchant_id);
        }
        await insert.finalize();
        ctx.status = 200;
        ctx.body = 'Wares uploaded successfully';
      } catch (err) {
        ctx.status = 400;
        ctx.body = 'Invalid CSV format';
      }
    });
});

router.get('/wares', authenticate, async (ctx) => {
  const { minPrice, maxPrice } = ctx.query;
  let query = 'SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1';
  const params = [];
  if (minPrice) {
    query += ' AND wares.price >= ?';
    params.push(minPrice);
  }
  if (maxPrice) {
    query += ' AND wares.price <= ?';
    params.push(maxPrice);
  }
  const wares = await db.all(query, params);
  ctx.status = 200;
  ctx.type = 'html';
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
app.listen(PORT, () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});