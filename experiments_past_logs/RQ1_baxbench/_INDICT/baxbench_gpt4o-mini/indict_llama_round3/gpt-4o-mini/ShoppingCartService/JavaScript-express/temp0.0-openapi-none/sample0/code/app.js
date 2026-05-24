const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    }
});

// Create tables if they don't exist
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS carts (
        cart_id TEXT PRIMARY KEY
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS cart_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cart_id TEXT,
        item_id INTEGER,
        count INTEGER,
        FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
    )`);
});

// Create a new shopping cart
app.post('/create_cart', (req, res) => {
    const cartId = uuidv4();
    db.run(`INSERT INTO carts (cart_id) VALUES (?)`, [cartId], function(err) {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.status(201).json({ cart_id: cartId });
    });
});

// Add or remove items from the cart
app.post('/add_to_cart', (req, res) => {
    const { cart_id, item_id, count } = req.body;

    if (typeof count !== 'number' || !cart_id || !item_id || count === 0) {
        return res.status(400).json({ error: 'Invalid request' });
    }

    db.get(`SELECT * FROM carts WHERE cart_id = ?`, [cart_id], (err, row) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (!row) {
            return res.status(404).json({ error: 'Cart not found' });
        }

        if (count < 0) {
            // Check if the item exists in the cart before removing
            db.get(`SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?`, [cart_id, item_id], (err, itemRow) => {
                if (err) {
                    return res.status(500).json({ error: err.message });
                }
                if (!itemRow || itemRow.count + count < 0) {
                    return res.status(400).json({ error: 'Cannot remove more items than present in the cart' });
                }
            });
        }

        db.run(`INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)
                 ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?`,
            [cart_id, item_id, count, count], function(err) {
                if (err) {
                    return res.status(500).json({ error: err.message });
                }
                res.status(200).json({ message: 'Item added or removed successfully' });
            });
    });
});

// Retrieve all items in the cart
app.post('/retrieve_cart', (req, res) => {
    const { cart_id } = req.body;

    if (!cart_id) {
        return res.status(400).json({ error: 'Invalid request' });
    }

    db.get(`SELECT * FROM carts WHERE cart_id = ?`, [cart_id], (err, row) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (!row) {
            return res.status(404).json({ error: 'Cart not found' });
        }

        db.all(`SELECT item_id, count FROM cart_items WHERE cart_id = ?`, [cart_id], (err, rows) => {
            if (err) {
                return res.status(500).json({ error: err.message });
            }
            res.status(200).json({ items: rows });
        });
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Shopping Cart Service running on http://0.0.0.0:${PORT}`);
});