const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');
const jwt = require('jsonwebtoken');
const cookieParser = require('cookie-parser');
const { v4: uuidv4 } = require('uuid');
const csvParser = require('csv-parser');
const multer = require('multer');
const fs = require('fs');
const path = require('path');

dotenv.config();

const app = express();
app.use(express.json());
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

const APP_SECRET = process.env.APP_SECRET || 'defaultsecret';

const authenticateToken = (req, res, next) => {
  const token = req.cookies.AUTH_COOKIE;
  if (!token) return res.sendStatus(401);

  jwt.verify(token, APP_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
};

app.post('/merchants/register', async (req, res) => {
  const { email, name, password } = req.body;
  if (!email || !name || !password) {
    return res.status(400).send('Invalid input');
  }

  const hashedPassword = await bcrypt.hash(password, 10);
  const id = uuidv4();

  db.run(`INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)`, [id, email, name, hashedPassword], function(err) {
    if (err) {
      return res.status(400).send('Error registering merchant');
    }
    res.status(201).send('Merchant registered successfully');
  });
});

app.post('/merchants/login', (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).send('Invalid input');
  }

  db.get(`SELECT * FROM merchants WHERE email = ?`, [email], async (err, merchant) => {
    if (err || !merchant) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    const match = await bcrypt.compare(password, merchant.password);
    if (!match) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    const token = jwt.sign({ id: merchant.id, email: merchant.email }, APP_SECRET, { expiresIn: '1h' });
    res.cookie('AUTH_COOKIE', token, { httpOnly: true, secure: true });
    res.status(200).json('Login successful');
  });
});

const upload = multer({ dest: 'uploads/' });

app.post('/merchants/upload-wares', authenticateToken, upload.single('csv'), (req, res) => {
  const filePath = req.file.path;
  const merchantId = req.user.id;

  const results = [];
  fs.createReadStream(filePath)
    .pipe(csvParser())
    .on('data', (data) => results.push(data))
    .on('end', () => {
      fs.unlinkSync(filePath); // Remove the file after processing
      const stmt = db.prepare(`INSERT INTO wares (id, name, description, price, merchant_id) VALUES (?, ?, ?, ?, ?)`);
      results.forEach((row) => {
        const id = uuidv4();
        stmt.run(id, row.name, row.description, parseFloat(row.price), merchantId);
      });
      stmt.finalize();
      res.status(200).send('Wares uploaded successfully');
    })
    .on('error', () => {
      res.status(400).send('Invalid CSV format');
    });
});

app.get('/wares', authenticateToken, (req, res) => {
  const { minPrice, maxPrice } = req.query;
  let query = `SELECT wares.name, wares.price, wares.description, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1`;
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
      return res.status(500).send('Error retrieving wares');
    }
    let html = '<table><tr><th>Name</th><th>Price</th><th>Description</th><th>Merchant Email</th></tr>';
    rows.forEach((row) => {
      html += `<tr><td>${row.name}</td><td>${row.price}</td><td>${row.description}</td><td>${row.email}</td></tr>`;
    });
    html += '</table>';
    res.status(200).send(html);
  });
});

app.listen(5000, '0.0.0.0', () => {
  console.log('Server is running on http://0.0.0.0:5000');
});