const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const PORT = 5000;

// Middleware to parse JSON bodies
app.use(express.json());

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        )`);
    }
});

// Endpoint to get recommended products by tags
app.get('/recommender', (req, res) => {
    const tags = req.query.tags;
    if (!tags) {
        return res.status(400).send('Tags are required');
    }

    const tagList = tags.split(',').map(tag => tag.trim());
    const placeholders = tagList.map(() => '?').join(',');
    const sql = `SELECT * FROM products WHERE tags LIKE '%' || ? || '%'`;

    db.all(sql, tagList, (err, rows) => {
        if (err) {
            return res.status(500).send('Database error');
        }
        const productsHtml = rows.map(row => `<div><h2>${row.product_name}</h2><p>Tags: ${row.tags}</p></div>`).join('');
        res.send(`<html><body>${productsHtml}</body></html>`);
    });
});

// Endpoint to post a new product
app.post('/recommender', (req, res) => {
    const { product_name, tags } = req.body;

    if (!product_name || !tags || !Array.isArray(tags)) {
        return res.status(400).send('Invalid input');
    }

    const tagsString = tags.join(',');
    const sql = `INSERT INTO products (product_name, tags) VALUES (?, ?)`;

    db.run(sql, [product_name, tagsString], function(err) {
        if (err) {
            return res.status(500).send('Database error');
        }
        res.status(200).send('Product added successfully');
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});