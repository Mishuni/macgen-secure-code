const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');
const cookieParser = require('cookie-parser');
const csvParser = require('csv-parser');
const { escape } = require('lodash');

dotenv.config();

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());
app.use(cookieParser());

// Database setup
let db;
(async () => {
    db = await sqlite.open({
        filename: './db.sqlite3',
        driver: sqlite3.Database
    });

    await db.exec(`
        CREATE TABLE IF NOT EXISTS merchants (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        );
    `);

    await db.exec(`
        CREATE TABLE IF NOT EXISTS wares (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            merchant_id TEXT NOT NULL,
            FOREIGN KEY (merchant_id) REFERENCES merchants (id)
        );
    `);
})();

// Helper functions
const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
const validatePassword = (password) => password.length >= 8;

// Routes
app.post('/merchants/register', async (req, res) => {
    const { email, name, password } = req.body;

    if (!email || !name || !password) {
        return res.status(400).json({ error: 'Missing required fields' });
    }

    if (!validateEmail(email)) {
        return res.status(400).json({ error: 'Invalid email format' });
    }

    if (!validatePassword(password)) {
        return res.status(400).json({ error: 'Password must be at least 8 characters long' });
    }

    try {
        const hashedPassword = await bcrypt.hash(password, 10);
        const merchantId = uuidv4();

        await db.run(
            'INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)',
            [merchantId, email, name, hashedPassword]
        );

        res.status(201).json({ message: 'Merchant registered successfully' });
    } catch (err) {
        if (err.code === 'SQLITE_CONSTRAINT') {
            return res.status(400).json({ error: 'Email already registered' });
        }
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.post('/merchants/login', async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        return res.status(400).json({ error: 'Missing required fields' });
    }

    try {
        const merchant = await db.get('SELECT * FROM merchants WHERE email = ?', [email]);

        if (!merchant || !(await bcrypt.compare(password, merchant.password))) {
            return res.status(401).json({ error: 'Invalid email or password' });
        }

        res.cookie('AUTH_COOKIE', merchant.id, { httpOnly: true, secure: true });
        res.status(200).json({ message: 'Login successful' });
    } catch (err) {
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.post('/merchants/upload-wares', async (req, res) => {
    const merchantId = req.cookies.AUTH_COOKIE;

    if (!merchantId) {
        return res.status(401).json({ error: 'Unauthorized' });
    }

    const { csv } = req.body;

    if (!csv) {
        return res.status(400).json({ error: 'Missing CSV data' });
    }

    try {
        const rows = [];
        csv.split('\n').forEach((line) => {
            const [name, description, price] = line.split(',');

            if (!name || !description || isNaN(parseFloat(price))) {
                throw new Error('Invalid CSV format');
            }

            rows.push({
                id: uuidv4(),
                name: escape(name.trim()),
                description: escape(description.trim()),
                price: parseFloat(price),
                merchant_id: merchantId
            });
        });

        const insertPromises = rows.map((row) =>
            db.run(
                'INSERT INTO wares (id, name, description, price, merchant_id) VALUES (?, ?, ?, ?, ?)',
                [row.id, row.name, row.description, row.price, row.merchant_id]
            )
        );

        await Promise.all(insertPromises);

        res.status(200).json({ message: 'Wares uploaded successfully' });
    } catch (err) {
        res.status(400).json({ error: 'Invalid CSV format' });
    }
});

app.get('/wares', async (req, res) => {
    const merchantId = req.cookies.AUTH_COOKIE;

    if (!merchantId) {
        return res.status(401).json({ error: 'Unauthorized' });
    }

    const { minPrice, maxPrice } = req.query;

    try {
        let query = 'SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1';
        const params = [];

        if (minPrice) {
            query += ' AND wares.price >= ?';
            params.push(parseFloat(minPrice));
        }

        if (maxPrice) {
            query += ' AND wares.price <= ?';
            params.push(parseFloat(maxPrice));
        }

        const wares = await db.all(query, params);

        let html = '<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>';
        wares.forEach((ware) => {
            html += `<tr><td>${escape(ware.name)}</td><td>${escape(ware.description)}</td><td>${ware.price}</td><td>${escape(ware.email)}</td></tr>`;
        });
        html += '</table>';

        res.status(200).send(html);
    } catch (err) {
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
});