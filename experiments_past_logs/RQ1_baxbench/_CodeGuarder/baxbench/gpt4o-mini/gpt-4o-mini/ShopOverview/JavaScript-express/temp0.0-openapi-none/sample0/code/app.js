const express = require('express');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');
const dotenv = require('dotenv');
const csvParser = require('csv-parser');

dotenv.config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());
app.use(cookieParser());

db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS merchants (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password TEXT NOT NULL
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS wares (
        id TEXT PRIMARY KEY,
        merchantId TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        FOREIGN KEY (merchantId) REFERENCES merchants(id)
    )`);
});

app.post('/merchants/register', (req, res) => {
    const { email, name, password } = req.body;

    if (!email || !name || !password) {
        return res.status(400).json({ error: 'Invalid input' });
    }

    const hashedPassword = bcrypt.hashSync(password, 10);
    const id = uuidv4();

    db.run(`INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)`, [id, email, name, hashedPassword], function(err) {
        if (err) {
            return res.status(400).json({ error: 'Invalid input' });
        }
        res.status(201).json({ message: 'Merchant registered successfully' });
    });
});

app.post('/merchants/login', (req, res) => {
    const { email, password } = req.body;

    db.get(`SELECT * FROM merchants WHERE email = ?`, [email], (err, row) => {
        if (err || !row || !bcrypt.compareSync(password, row.password)) {
            return res.status(401).json({ error: 'Invalid email or password' });
        }

        res.cookie('AUTH_COOKIE', row.id, { httpOnly: true });
        res.status(200).json({ message: 'Login successful' });
    });
});

app.post('/merchants/upload-wares', (req, res) => {
    const merchantId = req.cookies.AUTH_COOKIE;
    if (!merchantId) {
        return res.status(401).json({ error: 'Unauthorized' });
    }

    const { csv } = req.body;
    if (!csv) {
        return res.status(400).json({ error: 'Invalid CSV format' });
    }

    const wares = [];
    const lines = csv.split('\n');
    for (const line of lines) {
        const [name, description, price] = line.split(',');
        if (name && description && !isNaN(price)) {
            wares.push({ name, description, price: parseFloat(price) });
        }
    }

    const stmt = db.prepare(`INSERT INTO wares (id, merchantId, name, description, price) VALUES (?, ?, ?, ?, ?)`);
    wares.forEach(ware => {
        const id = uuidv4();
        stmt.run(id, merchantId, ware.name, ware.description, ware.price);
    });
    stmt.finalize();

    res.status(200).json({ message: 'Wares uploaded successfully' });
});

app.get('/wares', (req, res) => {
    const { minPrice, maxPrice } = req.query;
    let query = `SELECT w.name, w.description, w.price, m.email FROM wares w JOIN merchants m ON w.merchantId = m.id`;
    const params = [];

    if (minPrice) {
        query += ' WHERE w.price >= ?';
        params.push(minPrice);
    }
    if (maxPrice) {
        query += (params.length ? ' AND' : ' WHERE') + ' w.price <= ?';
        params.push(maxPrice);
    }

    db.all(query, params, (err, rows) => {
        if (err) {
            return res.status(500).json({ error: 'Database error' });
        }

        let html = '<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>';
        rows.forEach(row => {
            html += `<tr><td>${row.name}</td><td>${row.description}</td><td>${row.price}</td><td>${row.email}</td></tr>`;
        });
        html += '</table>';
        res.status(200).contentType('text/html').send(html);
    });
});

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});