const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const csvParser = require('csv-parser');
const fs = require('fs');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());
app.use(cookieParser());

// Initialize the database
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS merchants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password TEXT NOT NULL
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS wares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        merchant_id INTEGER,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        FOREIGN KEY (merchant_id) REFERENCES merchants(id)
    )`);
});

// Register a new merchant
app.post('/merchants/register', (req, res) => {
    const { email, name, password } = req.body;
    if (!email || !name || !password) {
        return res.status(400).json({ error: 'Invalid input' });
    }

    const stmt = db.prepare(`INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)`);
    stmt.run(email, name, password, function(err) {
        if (err) {
            return res.status(400).json({ error: 'Email already exists' });
        }
        res.status(201).json({ message: 'Merchant registered successfully' });
    });
    stmt.finalize();
});

// Merchant login
app.post('/merchants/login', (req, res) => {
    const { email, password } = req.body;
    if (!email || !password) {
        return res.status(400).json({ error: 'Invalid input' });
    }

    db.get(`SELECT * FROM merchants WHERE email = ? AND password = ?`, [email, password], (err, row) => {
        if (err || !row) {
            return res.status(401).json({ error: 'Invalid email or password' });
        }
        res.cookie('AUTH_COOKIE', 'some_auth_value'); // Set a cookie for the session
        res.status(200).json({ message: 'Login successful' });
    });
});

// Upload wares
app.post('/merchants/upload-wares', (req, res) => {
    const { csv } = req.body;
    if (!csv) {
        return res.status(400).json({ error: 'Invalid CSV format' });
    }

    const merchantId = 1; // This should be retrieved from the session in a real application
    const results = [];

    fs.createReadStream(csv)
        .pipe(csvParser())
        .on('data', (data) => results.push(data))
        .on('end', () => {
            const stmt = db.prepare(`INSERT INTO wares (merchant_id, name, description, price) VALUES (?, ?, ?, ?)`);
            results.forEach(ware => {
                stmt.run(merchantId, ware.name, ware.description, ware.price);
            });
            stmt.finalize();
            res.status(200).json({ message: 'Wares uploaded successfully' });
        });
});

// Retrieve all offered wares
app.get('/wares', (req, res) => {
    const { minPrice, maxPrice } = req.query;
    let query = `SELECT w.name, w.description, w.price, m.email FROM wares w JOIN merchants m ON w.merchant_id = m.id`;
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
        res.status(200).send(html);
    });
});

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});