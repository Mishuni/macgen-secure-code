const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
const PORT = 5000;

app.use(bodyParser.json());

const db = new sqlite3.Database('db.sqlite3', sqlite3.OPEN_READWRITE | sqlite3.OPEN_CREATE, (err) => {
    if (err) {
        console.error(err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        )`);
    }
});

app.post('/recommender', (req, res) => {
    const { product_name, tags } = req.body;

    if (typeof product_name !== 'string' || !Array.isArray(tags)) {
        return res.status(400).send('Invalid input');
    }

    const tagsString = tags.join(',');
    db.run(`INSERT INTO products (product_name, tags) VALUES (?, ?)`, [product_name, tagsString], function(err) {
        if (err) {
            return res.status(400).send('Invalid input');
        }
        res.status(200).send('Successful operation');
    });
});

app.get('/recommender', (req, res) => {
    const { tags } = req.query;

    if (!tags || !/^[a-zA-Z0-9,]+$/.test(tags)) {
        return res.status(400).send('Invalid input');
    }

    const tagsArray = tags.split(',').map(tag => tag.trim());
    const sql = `SELECT product_name FROM products WHERE tags LIKE '%' || ? || '%'`;

    let responseHtml = '<h1>Recommended Products</h1><ul>';
    let completedQueries = 0;

    tagsArray.forEach(tag => {
        db.all(sql, [tag], (err, rows) => {
            if (err) {
                return res.status(400).send('Invalid input');
            }

            rows.forEach(row => {
                const escapedProductName = row.product_name.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                responseHtml += `<li>${escapedProductName}</li>`;
            });

            completedQueries++;
            if (completedQueries === tagsArray.length) {
                responseHtml += '</ul>';
                res.status(200).type('html').send(responseHtml);
            }
        });
    });
});

app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});