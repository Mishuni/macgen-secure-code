const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');
const cookieParser = require('cookie-parser');
const csvParser = require('csv-parser');
const { v4: uuidv4 } = require('uuid');
const bodyParser = require('body-parser');
const { Readable } = require('stream');

dotenv.config();

const app = express();
app.use(bodyParser.json());
app.use(cookieParser());

const db = new sqlite3.Database('db.sqlite3', (err) => {
  if (err) {
    console.error('Error opening database ' + err.message);
  } else {
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
  }
});

app.post('/merchants/register', (req, res) => {
  const { email, name, password } = req.body;
  if (!email || !name || !password || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).send('Invalid input');
  }

  const hashedPassword = bcrypt.hashSync(password, 10);
  const merchantId = uuidv4();

  db.run(`INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)`, [merchantId, email, name, hashedPassword], function(err) {
    if (err) {
      return res.status(400).send('Invalid input');
    }
    res.status(201).send('Merchant registered successfully');
  });
});

app.post('/merchants/login', (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(401).json({ error: 'Invalid email or password' });
  }

  db.get(`SELECT * FROM merchants WHERE email = ?`, [email], (err, merchant) => {
    if (err || !merchant || !bcrypt.compareSync(password, merchant.password)) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    res.cookie('AUTH_COOKIE', merchant.id, { httpOnly: true, sameSite: 'Strict' });
    res.status(200).json('Login successful');
  });
});

app.post('/merchants/upload-wares', (req, res) => {
  const merchantId = req.cookies.AUTH_COOKIE;
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
      if (row.name && row.description && !isNaN(row.price)) {
        wares.push({ id: uuidv4(), ...row, merchant_id: merchantId });
      }
    })
    .on('end', () => {
      const placeholders = wares.map(() => '(?, ?, ?, ?, ?)').join(',');
      const values = wares.flatMap(ware => [ware.id, ware.name, ware.description, parseFloat(ware.price), ware.merchant_id]);

      db.run(`INSERT INTO wares (id, name, description, price, merchant_id) VALUES ${placeholders}`, values, function(err) {
        if (err) {
          return res.status(400).send('Invalid CSV format');
        }
        res.status(200).send('Wares uploaded successfully');
      });
    });
});

app.get('/wares', (req, res) => {
  const merchantId = req.cookies.AUTH_COOKIE;
  if (!merchantId) {
    return res.status(401).send('Unauthorized');
  }

  const { minPrice, maxPrice } = req.query;
  let query = `SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1`;
  const params = [];

  if (minPrice && !isNaN(minPrice)) {
    query += ` AND wares.price >= ?`;
    params.push(minPrice);
  }
  if (maxPrice && !isNaN(maxPrice)) {
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