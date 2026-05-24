const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json({ limit: '1mb' }));

// Create tables if they do not exist
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS carts (
        cart_id TEXT PRIMARY KEY
    )`);
    db.run(`CREATE TABLE IF NOT EXISTS cart_items (
        cart_id TEXT,
        item_id INTEGER,
        count INTEGER,
        PRIMARY KEY (cart_id, item_id),
        FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
    )`);
});

app.post('/create_cart', (req, res) => {
    const cart_id = uuidv4();
    db.run(`INSERT INTO carts (cart_id) VALUES (?)`, [cart_id], function(err) {
        if (err) {
            return res.status(500).json({ error: 'Failed to create cart' });
        }
        res.status(201).json({ cart_id });
    });
});

app.post('/add_to_cart', (req, res) => {
    const { cart_id, item_id, count } = req.body;

    if (!cart_id || typeof cart_id !== 'string') {
        return res.status(400).json({ error: 'Invalid cart_id' });
    }
    if (!Number.isInteger(item_id) || item_id <= 0) {
        return res.status(400).json({ error: 'Invalid item_id' });
    }
    if (!Number.isInteger(count)) {
        return res.status(400).json({ error: 'Invalid count' });
    }

    db.run(`INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)
            ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?`, 
            [cart_id, item_id, count, count], function(err) {
        if (err) {
            return res.status(500).json({ error: 'Failed to update cart' });
        }
        res.status(200).json({ message: 'Item added or removed successfully' });
    });
});

app.post('/retrieve_cart', (req, res) => {
    const { cart_id } = req.body;

    if (!cart_id || typeof cart_id !== 'string') {
        return res.status(400).json({ error: 'Invalid cart_id' });
    }

    db.all(`SELECT item_id, count FROM cart_items WHERE cart_id = ?`, [cart_id], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: 'Failed to retrieve cart' });
        }
        res.status(200).json({ items: rows });
    });
});

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});