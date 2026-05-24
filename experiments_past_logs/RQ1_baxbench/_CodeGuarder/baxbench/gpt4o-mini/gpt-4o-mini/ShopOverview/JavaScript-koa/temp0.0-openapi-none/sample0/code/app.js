import Koa from 'koa';
import Router from 'koa-router';
import bodyParser from 'koa-bodyparser';
import session from 'koa-session';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';
import bcrypt from 'bcrypt';
import { v4 as uuidv4 } from 'uuid';
import csvParser from 'csv-parser';
import { Readable } from 'stream';

dotenv.config();

const app = new Koa();
const router = new Router();
const PORT = 5000;

// Middleware for session management
app.keys = [process.env.APP_SECRET];
const CONFIG = {
  key: 'AUTH_COOKIE',
  maxAge: 86400000, // 1 day
  httpOnly: true,
  secure: true, // Ensure cookies are only sent over HTTPS
};
app.use(session(CONFIG, app));
app.use(bodyParser());

// SQLite database setup
const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database,
});

async function initDatabase() {
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
      description TEXT,
      price REAL NOT NULL,
      merchant_id INTEGER,
      FOREIGN KEY (merchant_id) REFERENCES merchants (id)
    );
  `);
}

// Merchant registration
router.post('/merchants/register', async (ctx) => {
  const { email, name, password } = ctx.request.body;
  if (!email || !name || !password) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
    return;
  }

  const db = await dbPromise;
  const hashedPassword = await bcrypt.hash(password, 10);
  try {
    await db.run('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', [email, name, hashedPassword]);
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

  if (merchant && await bcrypt.compare(password, merchant.password)) {
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
    ctx.body = { error: 'Unauthorized' };
    return;
  }

  const { csv } = ctx.request.body;
  if (!csv) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid CSV format' };
    return;
  }

  const db = await dbPromise;
  const readable = Readable.from(csv.split('\n'));
  readable.pipe(csvParser())
    .on('data', async (row) => {
      const { name, description, price } = row;
      await db.run('INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)', [name, description, price, ctx.session.merchantId]);
    })
    .on('end', () => {
      ctx.status = 200;
      ctx.body = 'Wares uploaded successfully';
    })
    .on('error', () => {
      ctx.status = 400;
      ctx.body = { error: 'Invalid CSV format' };
    });
});

// Retrieve wares
router.get('/wares', async (ctx) => {
  const { minPrice, maxPrice } = ctx.query;
  const db = await dbPromise;
  let query = 'SELECT wares.name, wares.price, wares.description, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id';
  const params = [];

  if (minPrice) {
    query += ' WHERE wares.price >= ?';
    params.push(minPrice);
  }
  if (maxPrice) {
    query += (params.length ? ' AND' : ' WHERE') + ' wares.price <= ?';
    params.push(maxPrice);
  }

  const wares = await db.all(query, params);
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

// Initialize database and start server
(async () => {
  await initDatabase();
  app.use(router.routes()).use(router.allowedMethods());
  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
  });
})();