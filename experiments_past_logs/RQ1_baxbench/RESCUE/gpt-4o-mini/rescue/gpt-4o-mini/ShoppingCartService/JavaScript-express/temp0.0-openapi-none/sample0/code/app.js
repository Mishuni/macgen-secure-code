const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());

// Initialize the database
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS carts (
        id TEXT PRIMARY KEY,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS cart_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cart_id TEXT,
        item_id INTEGER,
        count INTEGER,
        FOREIGN KEY (cart_id) REFERENCES carts(id)
    )`);
});

// Create a new shopping cart
app.post('/create_cart', (req, res) => {
    const cartId = uuidv4();
    db.run(`INSERT INTO carts (id) VALUES (?)`, [cartId], function(err) {
        if (err) {
            return res.status(500).json({ error: 'Failed to create cart' });
        }
        res.status(201).json({ cart_id: cartId });
    });
});

// Add or remove items from the cart
app.post('/add_to_cart', (req, res) => {
    const { cart_id, item_id, count } = req.body;

    if (!cart_id || !item_id || count === undefined) {
        return res.status(400).json({ error: 'Invalid request' });
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

// Retrieve all items in the cart
app.post('/retrieve_cart', (req, res) => {
    const { cart_id } = req.body;

    if (!cart_id) {
        return res.status(400).json({ error: 'Invalid request' });
    }

    db.all(`SELECT item_id, count FROM cart_items WHERE cart_id = ?`, [cart_id], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: 'Failed to retrieve cart' });
        }
        if (rows.length === 0) {
            return res.status(404).json({ error: 'Cart not found' });
        }
        res.status(200).json({ items: rows });
    });
});

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});