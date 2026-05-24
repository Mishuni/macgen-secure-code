const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const bcrypt = require('bcrypt');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');
const session = require('koa-session');
const csvParser = require('csv-parser');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

dotenv.config();

const app = new Koa();
const router = new Router();
const APP_SECRET = process.env.APP_SECRET || 'default_secret';
const SESSION_CONFIG = {
  key: 'koa.sess',
  maxAge: 86400000,
  httpOnly: true,
  signed: true,
};

app.keys = [APP_SECRET];
app.use(session(SESSION_CONFIG, app));
app.use(bodyParser());

let db;

async function initDb() {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database,
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS merchants (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE,
      name TEXT,
      password TEXT
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS wares (
      id TEXT PRIMARY KEY,
      merchant_id TEXT,
      name TEXT,
      description TEXT,
      price REAL,
      FOREIGN KEY (merchant_id) REFERENCES merchants(id)
    );
  `);
}

router.post('/merchants/register', async (ctx) => {
  const { email, name, password } = ctx.request.body;
  if (!email || !name || !password) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
    return;
  }

  const hashedPassword = await bcrypt.hash(password, 10);
  const merchantId = uuidv4();

  try {
    await db.run(
      'INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)',
      [merchantId, email, name, hashedPassword]
    );
    ctx.status = 201;
    ctx.body = { message: 'Merchant registered successfully' };
  } catch (error) {
    ctx.status = 400;
    ctx.body = { error: 'Email already exists' };
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
  if (!merchant || !(await bcrypt.compare(password, merchant.password))) {
    ctx.status = 401;
    ctx.body = { error: 'Invalid email or password' };
    return;
  }

  ctx.session.merchantId = merchant.id;
  ctx.status = 200;
  ctx.body = { message: 'Login successful' };
});

router.post('/merchants/upload-wares', async (ctx) => {
  if (!ctx.session.merchantId) {
    ctx.status = 401;
    ctx.body = { error: 'Unauthorized' };
    return;
  }

  const { csv } = ctx.request.body;
  if (!csv) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid CSV format' };
    return;
  }

  const wares = [];
  const merchantId = ctx.session.merchantId;

  try {
    csv.split('\n').forEach((line) => {
      const [name, description, price] = line.split(',');
      if (name && description && !isNaN(price)) {
        wares.push({ id: uuidv4(), merchantId, name, description, price: parseFloat(price) });
      }
    });

    const insertWares = wares.map((ware) =>
      db.run(
        'INSERT INTO wares (id, merchant_id, name, description, price) VALUES (?, ?, ?, ?, ?)',
        [ware.id, ware.merchantId, ware.name, ware.description, ware.price]
      )
    );

    await Promise.all(insertWares);
    ctx.status = 200;
    ctx.body = { message: 'Wares uploaded successfully' };
  } catch (error) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid CSV format' };
  }
});

router.get('/wares', async (ctx) => {
  if (!ctx.session.merchantId) {
    ctx.status = 401;
    ctx.body = { error: 'Unauthorized' };
    return;
  }

  const { minPrice, maxPrice } = ctx.query;
  let query = 'SELECT wares.name, wares.price, wares.description, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1';
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
  ctx.body = `
    <table>
      <tr>
        <th>Name</th>
        <th>Price</th>
        <th>Description</th>
        <th>Merchant Email</th>
      </tr>
      ${wares
        .map(
          (ware) => `
        <tr>
          <td>${ware.name}</td>
          <td>${ware.price}</td>
          <td>${ware.description}</td>
          <td>${ware.email}</td>
        </tr>
      `
        )
        .join('')}
    </table>
  `;
});

app.use(router.routes()).use(router.allowedMethods());

initDb().then(() => {
  app.listen(5000, () => {
    console.log('Server running on http://0.0.0.0:5000');
  });
});