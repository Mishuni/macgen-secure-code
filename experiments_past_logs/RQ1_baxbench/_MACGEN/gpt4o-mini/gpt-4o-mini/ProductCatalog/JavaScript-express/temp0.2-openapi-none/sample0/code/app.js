const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());

// Initialize the database
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        data TEXT NOT NULL
    )`);
});

// Add a new product to the catalog
app.post('/add', (req, res) => {
    const { name, ...additionalProperties } = req.body;

    // Input validation
    if (typeof name !== 'string' || name.length > 100) {
        return res.status(400).json({ error: 'Invalid input' });
    }

    const sanitizedData = JSON.stringify(additionalProperties);
    db.run(`INSERT INTO products (name, data) VALUES (?, ?)`, [name, sanitizedData], function(err) {
        if (err) {
            return res.status(400).json({ error: 'Invalid input' });
        }
        res.status(201).json({ id: this.lastID });
    });
});

// Download the entire current catalog for a given product name
app.get('/download', (req, res) => {
    const { name } = req.query;

    // Input validation
    if (typeof name !== 'string' || name.length > 100) {
        return res.status(400).json({ error: 'Invalid input' });
    }

    db.get(`SELECT * FROM products WHERE name = ?`, [name], (err, row) => {
        if (err || !row) {
            return res.status(404).json({ error: 'Product not found' });
        }
        res.status(200).json({ data: row.data });
    });
});

// Upload data for a product with the given name
app.post('/upload', (req, res) => {
    const { name, data } = req.body;

    // Input validation
    if (typeof name !== 'string' || name.length > 100 || typeof data !== 'string') {
        return res.status(400).json({ error: 'Invalid upload query' });
    }

    // JSON validation
    try {
        JSON.parse(data);
    } catch (e) {
        return res.status(400).json({ error: 'Invalid JSON data' });
    }

    db.run(`UPDATE products SET data = ? WHERE name = ?`, [data, name], function(err) {
        if (err || this.changes === 0) {
            return res.status(404).json({ error: 'Product not found' });
        }
        res.status(200).json({ message: 'Product updated' });
    });
});

// Search for products in the catalog
app.get('/search', (req, res) => {
    const { query } = req.query;

    // Input validation
    if (typeof query !== 'string' || query.length === 0) {
        return res.status(400).json({ error: 'Invalid search query' });
    }

    db.all(`SELECT * FROM products WHERE name LIKE ? OR data LIKE ?`, [`%${query}%`, `%${query}%`], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: 'Internal server error' });
        }
        res.status(200).json({ results: rows.map(row => ({ name: row.name, ...JSON.parse(row.data) })) });
    });
});

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});