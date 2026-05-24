const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');
const cookieParser = require('cookie-parser');
const { v4: uuidv4 } = require('uuid');
const bodyParser = require('body-parser');
const multer = require('multer');
const upload = multer();
const csvParser = require('csv-parser');
const { Readable } = require('stream');

dotenv.config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());
app.use(cookieParser(process.env.APP_SECRET));

// Initialize database
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS merchants (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    name TEXT,
    password TEXT
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS wares (
    id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    price REAL,
    merchant_id TEXT,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id)
  )`);
});

// Register a new merchant
app.post('/merchants/register', async (req, res) => {
  const { email, name, password } = req.body;
  if (!email || !name || !password) {
    return res.status(400).send('Invalid input');
  }

  const hashedPassword = await bcrypt.hash(password, 10);
  const merchantId = uuidv4();

  db.run(`INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)`, [merchantId, email, name, hashedPassword], function(err) {
    if (err) {
      return res.status(400).send('Invalid input');
    }
    res.status(201).send('Merchant registered successfully');
  });
});

// Merchant login
app.post('/merchants/login', (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(401).json({ error: 'Invalid email or password' });
  }

  db.get(`SELECT * FROM merchants WHERE email = ?`, [email], async (err, merchant) => {
    if (err || !merchant || !(await bcrypt.compare(password, merchant.password))) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    res.cookie('AUTH_COOKIE', merchant.id, { signed: true, httpOnly: true });
    res.status(200).json('Login successful');
  });
});

// Upload wares
app.post('/merchants/upload-wares', upload.none(), (req, res) => {
  const merchantId = req.signedCookies.AUTH_COOKIE;
  if (!merchantId) {
    return res.status(401).send('Unauthorized');
  }

  const { csv } = req.body;
  if (!csv) {
    return res.status(400).send('Invalid CSV format');
  }

  const wares = [];
  const stream = Readable.from(csv);
  stream.pipe(csvParser())
    .on('data', (row) => {
      const { name, description, price } = row;
      if (name && description && price && !isNaN(price)) {
        wares.push({ id: uuidv4(), name: name.trim(), description: description.trim(), price: parseFloat(price), merchant_id: merchantId });
      }
    })
    .on('end', () => {
      const stmt = db.prepare(`INSERT INTO wares (id, name, description, price, merchant_id) VALUES (?, ?, ?, ?, ?)`);
      wares.forEach(ware => {
        stmt.run(ware.id, ware.name, ware.description, ware.price, ware.merchant_id);
      });
      stmt.finalize();

      res.status(200).send('Wares uploaded successfully');
    })
    .on('error', () => {
      res.status(400).send('Invalid CSV format');
    });
});

// Retrieve wares
app.get('/wares', (req, res) => {
  const merchantId = req.signedCookies.AUTH_COOKIE;
  if (!merchantId) {
    return res.status(401).send('Unauthorized');
  }

  const { minPrice, maxPrice } = req.query;
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
      return res.status(500).send('Internal server error');
    }

    let html = '<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>';
    rows.forEach(row => {
      html += `<tr><td>${row.name}</td><td>${row.description}</td><td>${row.price}</td><td>${row.email}</td></tr>`;
    });
    html += '</table>';

    res.status(200).send(html);
  });
});

app.listen(5000, '0.0.0.0', () => {
  console.log('Server is running on http://0.0.0.0:5000');
});