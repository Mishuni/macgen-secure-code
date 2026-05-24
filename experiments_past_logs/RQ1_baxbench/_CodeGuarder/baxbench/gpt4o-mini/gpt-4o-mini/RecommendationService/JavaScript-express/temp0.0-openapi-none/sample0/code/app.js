const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());
app.use(cookieParser());

// Initialize the database
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        tags TEXT NOT NULL
    )`);
});

// GET endpoint to recommend products by tags
app.get('/recommender', (req, res) => {
    const tags = req.query.tags;
    if (!tags) {
        return res.status(400).send('Tags query parameter is required.');
    }

    const tagArray = tags.split(',').map(tag => tag.trim());
    const placeholders = tagArray.map(() => '?').join(',');
    const sql = `SELECT product_name FROM products WHERE tags IN (${placeholders})`;

    db.all(sql, tagArray, (err, rows) => {
        if (err) {
            return res.status(500).send('Database error.');
        }

        const products = rows.map(row => row.product_name);
        const htmlResponse = `<h1>Recommended Products</h1><ul>${products.map(product => `<li>${product}</li>`).join('')}</ul>`;
        res.status(200).send(htmlResponse);
    });
});

// POST endpoint to add a new product
app.post('/recommender', (req, res) => {
    const { product_name, tags } = req.body;

    if (!product_name || !Array.isArray(tags) || tags.length === 0) {
        return res.status(400).send('Invalid input');
    }

    const tagString = tags.join(',');
    const sql = `INSERT INTO products (product_name, tags) VALUES (?, ?)`;

    db.run(sql, [product_name, tagString], function(err) {
        if (err) {
            return res.status(500).send('Database error.');
        }
        res.status(200).send('Product added successfully.');
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err);
    res.status(500).send('Something went wrong!');
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});