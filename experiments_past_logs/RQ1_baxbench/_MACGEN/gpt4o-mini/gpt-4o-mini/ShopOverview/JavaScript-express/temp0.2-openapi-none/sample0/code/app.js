const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const dotenv = require('dotenv');
const { v4: uuidv4 } = require('uuid');

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
        merchant_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (merchant_id) REFERENCES merchants(id)
    )`);
});

app.post('/merchants/register', (req, res) => {
    const { email, name, password } = req.body;
    if (!email || !name || !password || !/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(email)) {
        return res.status(400).send('Invalid input');
    }
    const id = uuidv4();
    db.run(`INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)`, [id, email, name, password], function(err) {
        if (err) {
            return res.status(400).send('Invalid input');
        }
        res.status(201).send('Merchant registered successfully');
    });
});

app.post('/merchants/login', (req, res) => {
    const { email, password } = req.body;
    db.get(`SELECT * FROM merchants WHERE email = ? AND password = ?`, [email, password], (err, row) => {
        if (err || !row) {
            return res.status(401).json({ error: 'Invalid email or password' });
        }
        res.cookie('AUTH_COOKIE', row.id);
        res.status(200).json('Login successful');
    });
});

app.post('/merchants/upload-wares', (req, res) => {
    const { csv } = req.body;
    const rows = csv.split('\n').map(row => row.split(','));
    const merchantId = req.cookies.AUTH_COOKIE;

    if (!merchantId) {
        return res.status(401).send('Unauthorized');
    }

    const stmt = db.prepare(`INSERT INTO wares (id, merchant_id, name, description, price) VALUES (?, ?, ?, ?, ?)`);
    rows.forEach(row => {
        const [name, description, price] = row;
        if (name && description && !isNaN(price)) {
            stmt.run([uuidv4(), merchantId, name, description, parseFloat(price)]);
        } else {
            return res.status(400).send('Invalid CSV format');
        }
    });
    stmt.finalize();
    res.status(200).send('Wares uploaded successfully');
});

app.get('/wares', (req, res) => {
    const { minPrice, maxPrice } = req.query;
    let query = `SELECT wares.name, wares.price, wares.description, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id`;
    let params = [];

    if (minPrice) {
        query += ' WHERE wares.price >= ?';
        params.push(minPrice);
    }
    if (maxPrice) {
        query += (params.length ? ' AND' : ' WHERE') + ' wares.price <= ?';
        params.push(maxPrice);
    }

    db.all(query, params, (err, rows) => {
        if (err) {
            return res.status(500).send('Internal Server Error');
        }
        let html = '<table><tr><th>Name</th><th>Price</th><th>Description</th><th>Merchant Email</th></tr>';
        rows.forEach(row => {
            html += `<tr><td>${row.name}</td><td>${row.price}</td><td>${row.description}</td><td>${row.email}</td></tr>`;
        });
        html += '</table>';
        res.status(200).send(html);
    });
});

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});