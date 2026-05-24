const express = require('express');
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const cookieParser = require('cookie-parser');
const { v4: uuidv4 } = require('uuid');
const helmet = require('helmet');
const xss = require('xss');
const csrf = require('csurf');

dotenv.config();

const app = express();
app.use(express.json());
app.use(cookieParser());
app.use(helmet());

const csrfProtection = csrf({ cookie: true });
app.use(csrfProtection);

const APP_SECRET = process.env.APP_SECRET;
if (!APP_SECRET) {
  throw new Error('APP_SECRET environment variable is not set');
}
const PORT = process.env.PORT || 5000;
const HOST = process.env.HOST || '127.0.0.1';

// Initialize SQLite database
let db;
(async () => {
  db = await sqlite.open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

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
})();

// Helper function to authenticate merchants
async function authenticateMerchant(req, res, next) {
  const authCookie = req.cookies.AUTH_COOKIE;
  if (!authCookie) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  const merchant = await db.get('SELECT * FROM merchants WHERE id = ?', [authCookie]);
  if (!merchant) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  req.merchant = merchant;
  next();
}

// Register a new merchant
app.post('/merchants/register', async (req, res) => {
  const { email, name, password } = req.body;
  if (!email || !name || !password) {
    return res.status(400).json({ error: 'Invalid input' });
  }

  const hashedPassword = await bcrypt.hash(password, 12);
  const merchantId = uuidv4();

  try {
    await db.run('INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)', [merchantId, email, name, hashedPassword]);
    res.status(201).send('Merchant registered successfully');
  } catch (err) {
    res.status(400).json({ error: 'Email already exists or invalid input' });
  }
});

// Merchant login
app.post('/merchants/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(401).json({ error: 'Invalid email or password' });
  }

  const merchant = await db.get('SELECT * FROM merchants WHERE email = ?', [email]);
  if (!merchant || !(await bcrypt.compare(password, merchant.password))) {
    return res.status(401).json({ error: 'Invalid email or password' });
  }

  res.cookie('AUTH_COOKIE', merchant.id, { httpOnly: true, secure: process.env.NODE_ENV === 'production', sameSite: 'Strict' });
  res.status(200).json('Login successful');
});

// Upload wares
app.post('/merchants/upload-wares', authenticateMerchant, async (req, res) => {
  const { csv } = req.body;
  if (!csv) {
    return res.status(400).json({ error: 'Invalid CSV format' });
  }

  const wares = [];
  csv.split('\n').forEach(line => {
    const [name, description, price] = line.split(',');
    if (name && description && price && !isNaN(price)) {
      wares.push({ id: uuidv4(), merchant_id: req.merchant.id, name: xss(name), description: xss(description), price: parseFloat(price) });
    }
  });

  try {
    const insertWares = wares.map(ware => db.run('INSERT INTO wares (id, merchant_id, name, description, price) VALUES (?, ?, ?, ?, ?)', [ware.id, ware.merchant_id, ware.name, ware.description, ware.price]));
    await Promise.all(insertWares);
    res.status(200).send('Wares uploaded successfully');
  } catch (err) {
    res.status(400).json({ error: 'Invalid CSV format' });
  }
});

// Retrieve wares
app.get('/wares', authenticateMerchant, async (req, res) => {
  const { minPrice, maxPrice } = req.query;
  let query = 'SELECT wares.name, wares.price, wares.description, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1';
  const params = [];

  if (minPrice && !isNaN(minPrice)) {
    query += ' AND wares.price >= ?';
    params.push(parseFloat(minPrice));
  }
  if (maxPrice && !isNaN(maxPrice)) {
    query += ' AND wares.price <= ?';
    params.push(parseFloat(maxPrice));
  }

  const wares = await db.all(query, params);
  let html = '<table><tr><th>Name</th><th>Price</th><th>Description</th><th>Merchant Email</th></tr>';
  wares.forEach(ware => {
    html += `<tr><td>${xss(ware.name)}</td><td>${xss(ware.price)}</td><td>${xss(ware.description)}</td><td>${xss(ware.email)}</td></tr>`;
  });
  html += '</table>';

  res.setHeader('Content-Type', 'text/html');
  res.status(200).send(html);
});

app.listen(PORT, HOST, () => {
  console.log(`Server running on http://${HOST}:${PORT}`);
});