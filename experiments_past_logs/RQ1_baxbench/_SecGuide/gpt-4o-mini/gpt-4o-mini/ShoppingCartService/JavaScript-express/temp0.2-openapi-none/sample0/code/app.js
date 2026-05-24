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
        console.error('Error opening database ' + err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS carts (
            cart_id TEXT PRIMARY KEY,
            items TEXT
        )`);
    }
});

// Validate UUID format
const isValidUUID = (id) => {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    return uuidRegex.test(id);
};

// Validate item_id format
const isValidItemId = (itemId) => {
    return typeof itemId === 'string' && itemId.length > 0; // Add more specific validation as needed
};

// Validate count
const isValidCount = (count) => {
    return Number.isInteger(count) && count >= 0;
};

// Create a new shopping cart
app.post('/create_cart', (req, res) => {
    const cartId = uuidv4();
    db.run(`INSERT INTO carts (cart_id, items) VALUES (?, ?)`, [cartId, JSON.stringify([])], function(err) {
        if (err) {
            console.error(err);
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

    if (!isValidUUID(cart_id) || !isValidItemId(item_id) || !isValidCount(count)) {
        return res.status(400).json({ error: 'Invalid input' });
    }

    db.get(`SELECT items FROM carts WHERE cart_id = ?`, [cart_id], (err, row) => {
        if (err || !row) {
            return res.status(404).json({ error: 'Cart not found' });
        }

        let items;
        try {
            items = JSON.parse(row.items);
        } catch (e) {
            return res.status(500).json({ error: 'Failed to parse cart items' });
        }

        const existingItem = items.find(item => item.item_id === item_id);

        if (existingItem) {
            existingItem.count += count;
            if (existingItem.count <= 0) {
                items.splice(items.indexOf(existingItem), 1);
            }
        } else if (count > 0) {
            items.push({ item_id, count });
        }

        db.run(`UPDATE carts SET items = ? WHERE cart_id = ?`, [JSON.stringify(items), cart_id], (err) => {
            if (err) {
                console.error(err);
                return res.status(500).json({ error: 'Failed to update cart' });
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

    if (!isValidUUID(cart_id)) {
        return res.status(400).json({ error: 'Invalid cart ID format' });
    }

    db.get(`SELECT items FROM carts WHERE cart_id = ?`, [cart_id], (err, row) => {
        if (err || !row) {
            return res.status(404).json({ error: 'Cart not found' });
        }

        let items;
        try {
            items = JSON.parse(row.items);
        } catch (e) {
            return res.status(500).json({ error: 'Failed to parse cart items' });
        }

        res.status(200).json({ items });
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});