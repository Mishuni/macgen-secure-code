const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const bcrypt = require('bcrypt');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const dotenv = require('dotenv');
const session = require('koa-session');
const csvParser = require('csv-parser');
const { v4: uuidv4 } = require('uuid');
const fs = require('fs');
const https = require('https');
const validator = require('validator');
const escapeHtml = require('escape-html');
const rateLimit = require('koa-ratelimit');

dotenv.config();

const app = new Koa();
const router = new Router();
const dbPromise = sqlite.open({ filename: 'db.sqlite3', driver: sqlite3.Database });

app.keys = [process.env.APP_SECRET];
app.use(session({
  key: 'koa.sess',
  maxAge: 86400000,
  httpOnly: true,
  secure: true,
  sameSite: 'lax'
}, app));
app.use(bodyParser());

// Rate limiting middleware
app.use(rateLimit({
  driver: 'memory',
  db: new Map(),
  duration: 60000,
  errorMessage: 'Too many requests, please try again later.',
  max: 100,
  disableHeader: false,
}));

async function initDb() {
  const db = await dbPromise;
  await db.run(`CREATE TABLE IF NOT EXISTS merchants (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    name TEXT,
    password TEXT
  )`);
  await db.run(`CREATE TABLE IF NOT EXISTS wares (
    id TEXT PRIMARY KEY,
    merchant_id TEXT,
    name TEXT,
    description TEXT,
    price REAL,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id)
  )`);
}

router.post('/merchants/register', async (ctx) => {
  const { email, name, password } = ctx.request.body;
  if (!email || !name || !password || !validator.isEmail(email) || !validator.isStrongPassword(password)) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  const hashedPassword = await bcrypt.hash(password, 12); // Increased bcrypt work factor
  const db = await dbPromise;
  try {
    await db.run('INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)', [uuidv4(), email, name, hashedPassword]);
    ctx.status = 201;
    ctx.body = 'Merchant registered successfully';
  } catch (error) {
    ctx.status = 400;
    ctx.body = 'Email already exists';
  }
});

router.post('/merchants/login', async (ctx) => {
  const { email, password } = ctx.request.body;
  if (!email || !password) {
    ctx.status = 401;
    ctx.body = { error: 'Invalid email or password' };
    return;
  }

  const db = await dbPromise;
  const merchant = await db.get('SELECT * FROM merchants WHERE email = ?', [email]);

  if (merchant && await bcrypt.compare(password, merchant.password)) {
    ctx.session.regenerateId(); // Regenerate session ID to prevent session fixation
    ctx.session.merchantId = merchant.id;
    ctx.status = 200;
    ctx.body = 'Login successful';
  } else {
    ctx.status = 401;
    ctx.body = { error: 'Invalid email or password' };
  }
});

router.post('/merchants/upload-wares', async (ctx) => {
  if (!ctx.session.merchantId) {
    ctx.status = 401;
    ctx.body = 'Unauthorized';
    return;
  }

  const { csv } = ctx.request.body;
  if (!csv) {
    ctx.status = 400;
    ctx.body = 'Invalid CSV format';
    return;
  }

  const db = await dbPromise;
  const merchantId = ctx.session.merchantId;
  const wares = [];

  csv.split('\n').forEach(line => {
    const [name, description, price] = line.split(',');
    if (name && description && price && !isNaN(price)) {
      wares.push({ id: uuidv4(), merchant_id: merchantId, name: validator.escape(name), description: validator.escape(description), price: parseFloat(price) });
    }
  });

  try {
    const insertWares = await db.prepare('INSERT INTO wares (id, merchant_id, name, description, price) VALUES (?, ?, ?, ?, ?)');
    for (const ware of wares) {
      await insertWares.run(ware.id, ware.merchant_id, ware.name, ware.description, ware.price);
    }
    await insertWares.finalize();
    ctx.status = 200;
    ctx.body = 'Wares uploaded successfully';
  } catch (error) {
    ctx.status = 400;
    ctx.body = 'Error uploading wares';
  }
});

router.get('/wares', async (ctx) => {
  if (!ctx.session.merchantId) {
    ctx.status = 401;
    ctx.body = 'Unauthorized';
    return;
  }

  const minPrice = parseFloat(ctx.query.minPrice) || 0;
  const maxPrice = parseFloat(ctx.query.maxPrice) || Number.MAX_VALUE;

  const db = await dbPromise;
  const wares = await db.all(
    `SELECT wares.name, wares.price, wares.description 
     FROM wares 
     WHERE wares.price BETWEEN ? AND ?`,
    [minPrice, maxPrice]
  );

  ctx.status = 200;
  ctx.type = 'html';
  ctx.body = `
    <table>
      <tr>
        <th>Name</th>
        <th>Price</th>
        <th>Description</th>
      </tr>
      ${wares.map(ware => `
        <tr>
          <td>${escapeHtml(ware.name)}</td>
          <td>${escapeHtml(ware.price.toString())}</td>
          <td>${escapeHtml(ware.description)}</td>
        </tr>
      `).join('')}
    </table>
  `;
});

app.use(router.routes()).use(router.allowedMethods());

initDb().then(() => {
  const options = {
    key: fs.readFileSync('server.key'),
    cert: fs.readFileSync('server.cert')
  };
  https.createServer(options, app.callback()).listen(5000, '0.0.0.0', () => {
    console.log('Server running on https://0.0.0.0:5000');
  });
});