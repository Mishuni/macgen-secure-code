const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');
const csvParser = require('csv-parser');
const { Readable } = require('stream');
const jwt = require('jsonwebtoken');
const session = require('koa-session');

dotenv.config();

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

const APP_SECRET = process.env.APP_SECRET || 'default_secret';

// Middleware
app.use(bodyParser());
app.keys = [APP_SECRET];
app.use(session(app));

// Initialize database
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS merchants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    name TEXT,
    password TEXT
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS wares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    price REAL,
    merchant_id INTEGER,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id)
  )`);
});

// Helper function to parse CSV
function parseCSV(csvString) {
  return new Promise((resolve, reject) => {
    const results = [];
    const stream = Readable.from([csvString]);
    stream
      .pipe(csvParser())
      .on('data', (data) => results.push(data))
      .on('end', () => resolve(results))
      .on('error', (err) => reject(err));
  });
}

// Authentication middleware
async function authenticate(ctx, next) {
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
}

// Routes
router.post('/merchants/register', async (ctx) => {
  const { email, name, password } = ctx.request.body;
  if (!email || !name || !password) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  const hashedPassword = await bcrypt.hash(password, 10);

  db.run(
    `INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)`,
    [email, name, hashedPassword],
    function (err) {
      if (err) {
        ctx.status = 400;
        ctx.body = 'Invalid input';
      } else {
        ctx.status = 201;
        ctx.body = 'Merchant registered successfully';
      }
    }
  );
});

router.post('/merchants/login', async (ctx) => {
  const { email, password } = ctx.request.body;
  if (!email || !password) {
    ctx.status = 401;
    ctx.body = { error: 'Invalid email or password' };
    return;
  }

  db.get(
    `SELECT * FROM merchants WHERE email = ?`,
    [email],
    async (err, merchant) => {
      if (err || !merchant) {
        ctx.status = 401;
        ctx.body = { error: 'Invalid email or password' };
      } else {
        const match = await bcrypt.compare(password, merchant.password);
        if (match) {
          const token = jwt.sign({ id: merchant.id }, APP_SECRET, { expiresIn: '1h' });
          ctx.cookies.set('AUTH_COOKIE', token, { httpOnly: true });
          ctx.status = 200;
          ctx.body = 'Login successful';
        } else {
          ctx.status = 401;
          ctx.body = { error: 'Invalid email or password' };
        }
      }
    }
  );
});

router.post('/merchants/upload-wares', authenticate, async (ctx) => {
  const { csv } = ctx.request.body;
  if (!csv) {
    ctx.status = 400;
    ctx.body = 'Invalid CSV format';
    return;
  }

  try {
    const wares = await parseCSV(csv);
    const merchantId = ctx.state.merchantId;

    const stmt = db.prepare(
      `INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)`
    );

    wares.forEach((ware) => {
      stmt.run(ware.name, ware.description, parseFloat(ware.price), merchantId);
    });

    stmt.finalize();

    ctx.status = 200;
    ctx.body = 'Wares uploaded successfully';
  } catch (error) {
    ctx.status = 400;
    ctx.body = 'Invalid CSV format';
  }
});

router.get('/wares', authenticate, async (ctx) => {
  const { minPrice, maxPrice } = ctx.query;
  let query = `SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1`;
  const params = [];

  if (minPrice) {
    query += ` AND wares.price >= ?`;
    params.push(minPrice);
  }

  if (maxPrice) {
    query += ` AND wares.price <= ?`;
    params.push(maxPrice);
  }

  db.all(query, params, (err, rows) => {
    if (err) {
      ctx.status = 500;
      ctx.body = 'Internal server error';
    } else {
      let html = '<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>';
      rows.forEach((row) => {
        html += `<tr><td>${row.name}</td><td>${row.description}</td><td>${row.price}</td><td>${row.email}</td></tr>`;
      });
      html += '</table>';
      ctx.status = 200;
      ctx.body = html;
    }
  });
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});