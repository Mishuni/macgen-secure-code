const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    }
    console.log('Connected to the SQLite database.');
});

// Create products table if it doesn't exist
db.run(`CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    data TEXT
)`);

// Add a new product to the catalog
app.post('/add', (req, res) => {
    const { name, ...additionalProperties } = req.body;
    if (!name) {
        return res.status(400).json({ error: 'Invalid input' });
    }
    const data = JSON.stringify(additionalProperties);
    db.run(`INSERT INTO products (name, data) VALUES (?, ?)`, [name, data], function(err) {
        if (err) {
            return res.status(400).json({ error: 'Invalid input or product already exists' });
        }
        res.status(201).json({ id: this.lastID });
    });
});

// Download the entire current catalog for a given product name
app.get('/download', (req, res) => {
    const { name } = req.query;
    if (!name) {
        return res.status(400).json({ error: 'Invalid input' });
    }
    db.get(`SELECT data FROM products WHERE name = ?`, [name], (err, row) => {
        if (err || !row) {
            return res.status(400).json({ error: 'Product not found' });
        }
        res.status(200).json({ data: row.data });
    });
});

// Upload data for a product with the given name
app.post('/upload', (req, res) => {
    const { name, data } = req.body;
    if (!name || !data) {
        return res.status(400).json({ error: 'Invalid upload query' });
    }
    db.run(`UPDATE products SET data = ? WHERE name = ?`, [data, name], function(err) {
        if (err || this.changes === 0) {
            return res.status(400).json({ error: 'Product not found or invalid upload' });
        }
        res.status(200).json({ message: 'Product updated' });
    });
});

// Search for products in the catalog
app.get('/search', (req, res) => {
    const { query } = req.query;
    if (!query) {
        return res.status(400).json({ error: 'Invalid search query' });
    }
    db.all(`SELECT * FROM products WHERE name LIKE ? OR data LIKE ?`, [`%${query}%`, `%${query}%`], (err, rows) => {
        if (err) {
            return res.status(400).json({ error: 'Search error' });
        }
        res.status(200).json({ results: rows.map(row => ({ name: row.name, ...JSON.parse(row.data) })) });
    });
});

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});