const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

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

// Get products by tags
app.get('/recommender', (req, res) => {
    const tags = req.query.tags;
    if (!tags) {
        return res.status(400).send('Tags are required');
    }

    const tagArray = tags.split(',').map(tag => tag.trim());
    const placeholders = tagArray.map(() => '?').join(',');
    const sql = `SELECT * FROM products WHERE tags LIKE '%' || ? || '%' OR tags LIKE '%' || ? || '%' OR tags LIKE '%' || ? || '%'`;

    db.all(sql, tagArray, (err, rows) => {
        if (err) {
            return res.status(500).send('Error retrieving products');
        }

        const productsHtml = rows.map(row => `<div><h2>${row.product_name}</h2><p>Tags: ${row.tags}</p></div>`).join('');
        res.set('Content-Type', 'text/html');
        res.send(productsHtml);
    });
});

// Post a new product
app.post('/recommender', (req, res) => {
    const { product_name, tags } = req.body;

    if (!product_name || !tags || !Array.isArray(tags)) {
        return res.status(400).send('Invalid input');
    }

    const tagsString = tags.join(',');
    const sql = `INSERT INTO products (product_name, tags) VALUES (?, ?)`;

    db.run(sql, [product_name, tagsString], function(err) {
        if (err) {
            return res.status(500).send('Error posting product');
        }
        res.status(200).send('Product posted successfully');
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});