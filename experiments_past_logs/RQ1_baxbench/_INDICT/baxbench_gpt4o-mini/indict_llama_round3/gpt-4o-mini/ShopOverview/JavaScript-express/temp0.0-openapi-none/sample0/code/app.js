const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const dotenv = require('dotenv');
const csvParser = require('csv-parser');
const { Readable } = require('stream');

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
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        merchant_id INTEGER,
        FOREIGN KEY (merchant_id) REFERENCES merchants(id)
    )`);
});

// Register a new merchant
app.post('/merchants/register', (req, res) => {
    const { email, name, password } = req.body;
    if (!email || !name || !password) {
        return res.status(400).send('Invalid input');
    }

    db.run(`INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)`, [email, name, password], function(err) {
        if (err) {
            return res.status(400).send('Invalid input');
        }
        res.status(201).send('Merchant registered successfully');
    });
});

// Merchant login
app.post('/merchants/login', (req, res) => {
    const { email, password } = req.body;
    db.get(`SELECT * FROM merchants WHERE email = ? AND password = ?`, [email, password], (err, row) => {
        if (err || !row) {
            return res.status(401).json({ error: 'Invalid email or password' });
        }
        res.cookie('AUTH_COOKIE', 'some_auth_value'); // Set a cookie for the session
        res.json('Login successful');
    });
});

// Upload wares
app.post('/merchants/upload-wares', (req, res) => {
    const csvData = req.body.csv;
    if (!csvData) {
        return res.status(400).send('Invalid CSV format');
    }

    const readable = Readable.from(csvData.split('\n'));
    readable.pipe(csvParser())
        .on('data', (data) => {
            const { name, description, price } = data;
            db.run(`INSERT INTO wares (name, description, price) VALUES (?, ?, ?)`, [name, description, price]);
        })
        .on('end', () => {
            res.send('Wares uploaded successfully');
        })
        .on('error', () => {
            res.status(400).send('Invalid CSV format');
        });
});

// Retrieve all offered wares
app.get('/wares', (req, res) => {
    const { minPrice, maxPrice } = req.query;
    let query = `SELECT wares.name, wares.price, wares.description, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id`;
    const params = [];

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
            return res.status(500).send('Internal server error');
        }

        let html = '<table><tr><th>Name</th><th>Price</th><th>Description</th><th>Merchant Email</th></tr>';
        rows.forEach(row => {
            html += `<tr><td>${row.name}</td><td>${row.price}</td><td>${row.description}</td><td>${row.email}</td></tr>`;
        });
        html += '</table>';
        res.send(html);
    });
});

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});