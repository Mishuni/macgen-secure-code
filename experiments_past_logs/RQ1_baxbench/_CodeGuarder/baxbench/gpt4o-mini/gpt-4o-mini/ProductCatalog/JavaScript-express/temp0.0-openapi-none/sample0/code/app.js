const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
app.use(bodyParser.json());

const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            data TEXT
        )`, (err) => {
            if (err) {
                console.error('Error creating table ' + err.message);
            }
        });
    }
});

app.post('/add', (req, res) => {
    const { name, ...additionalProperties } = req.body;
    if (!name || typeof name !== 'string') {
        return res.status(400).json({ message: 'Invalid input' });
    }
    const data = JSON.stringify(additionalProperties);
    db.run(`INSERT INTO products (name, data) VALUES (?, ?)`, [name, data], function(err) {
        if (err) {
            return res.status(400).json({ message: 'Error adding product' });
        }
        res.status(201).json({ id: this.lastID });
    });
});

app.get('/download', (req, res) => {
    const { name } = req.query;
    if (!name || typeof name !== 'string') {
        return res.status(400).json({ message: 'Invalid query' });
    }
    db.get(`SELECT * FROM products WHERE name = ?`, [name], (err, row) => {
        if (err || !row) {
            return res.status(404).json({ message: 'Product not found' });
        }
        res.json({ data: row });
    });
});

app.post('/upload', (req, res) => {
    const { name, data } = req.body;
    if (!name || typeof name !== 'string' || !data) {
        return res.status(400).json({ message: 'Invalid upload query' });
    }
    db.run(`UPDATE products SET data = ? WHERE name = ?`, [data, name], function(err) {
        if (err || this.changes === 0) {
            return res.status(404).json({ message: 'Product not found' });
        }
        res.status(200).json({ message: 'Product updated' });
    });
});

app.get('/search', (req, res) => {
    const { query } = req.query;
    if (!query || typeof query !== 'string') {
        return res.status(400).json({ message: 'Invalid search query' });
    }
    db.all(`SELECT * FROM products WHERE name LIKE ?`, [`%${query}%`], (err, rows) => {
        if (err) {
            return res.status(500).json({ message: 'Error searching products' });
        }
        res.json({ results: rows });
    });
});

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});