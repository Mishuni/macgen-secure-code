const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());

// Initialize the database schema
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS carts (
        id TEXT PRIMARY KEY
    )`);
    db.run(`CREATE TABLE IF NOT EXISTS cart_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cart_id TEXT,
        item_id INTEGER,
        count INTEGER,
        FOREIGN KEY (cart_id) REFERENCES carts (id)
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

    if (!cart_id || typeof item_id !== 'number' || typeof count !== 'number') {
        return res.status(400).json({ error: 'Invalid request' });
    }

    db.get(`SELECT * FROM carts WHERE id = ?`, [cart_id], (err, row) => {
        if (err || !row) {
            return res.status(404).json({ error: 'Cart not found' });
        }

        if (count < 0) {
            db.run(`DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?`, [cart_id, item_id], function(err) {
                if (err) {
                    return res.status(500).json({ error: 'Failed to remove item' });
                }
                return res.status(200).json({ message: 'Item removed successfully' });
            });
        } else {
            db.run(`INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?`, [cart_id, item_id, count, count], function(err) {
                if (err) {
                    return res.status(500).json({ error: 'Failed to add item' });
                }
                return res.status(200).json({ message: 'Item added successfully' });
            });
        }
    });
});

// Retrieve all items in the cart
app.post('/retrieve_cart', (req, res) => {
    const { cart_id } = req.body;

    if (!cart_id) {
        return res.status(400).json({ error: 'Invalid request' });
    }

    db.get(`SELECT * FROM carts WHERE id = ?`, [cart_id], (err, row) => {
        if (err || !row) {
            return res.status(404).json({ error: 'Cart not found' });
        }

        db.all(`SELECT item_id, count FROM cart_items WHERE cart_id = ?`, [cart_id], (err, items) => {
            if (err) {
                return res.status(500).json({ error: 'Failed to retrieve items' });
            }
            res.status(200).json({ items });
        });
    });
});

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});