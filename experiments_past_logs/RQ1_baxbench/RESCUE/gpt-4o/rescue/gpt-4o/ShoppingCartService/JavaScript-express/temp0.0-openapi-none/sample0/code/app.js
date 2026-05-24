const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const bodyParser = require('body-parser');

// Initialize Express app
const app = express();
app.use(bodyParser.json());

// Database setup
const dbFile = 'db.sqlite3';
let db;

// Initialize SQLite database
(async () => {
    db = await open({
        filename: dbFile,
        driver: sqlite3.Database
    });

    // Create tables if they don't exist
    await db.exec(`
        CREATE TABLE IF NOT EXISTS carts (
            id TEXT PRIMARY KEY
        );
    `);

    await db.exec(`
        CREATE TABLE IF NOT EXISTS cart_items (
            cart_id TEXT,
            item_id INTEGER,
            count INTEGER,
            PRIMARY KEY (cart_id, item_id),
            FOREIGN KEY (cart_id) REFERENCES carts(id)
        );
    `);
})();

// Helper function to validate input
function validateInput(input, requiredFields) {
    for (const field of requiredFields) {
        if (!input.hasOwnProperty(field)) {
            return false;
        }
    }
    return true;
}

// API to create a new shopping cart
app.post('/create_cart', async (req, res) => {
    try {
        const cartId = uuidv4();
        await db.run('INSERT INTO carts (id) VALUES (?)', [cartId]);
        res.status(201).json({ cart_id: cartId });
    } catch (error) {
        console.error('Error creating cart:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

// API to add or remove items from the cart
app.post('/add_to_cart', async (req, res) => {
    try {
        const { cart_id, item_id, count } = req.body;

        // Validate input
        if (!validateInput(req.body, ['cart_id', 'item_id', 'count'])) {
            return res.status(400).json({ error: 'Invalid request' });
        }

        // Check if cart exists
        const cart = await db.get('SELECT id FROM carts WHERE id = ?', [cart_id]);
        if (!cart) {
            return res.status(404).json({ error: 'Cart not found' });
        }

        // Check if item already exists in the cart
        const existingItem = await db.get(
            'SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?',
            [cart_id, item_id]
        );

        if (existingItem) {
            const newCount = existingItem.count + count;

            if (newCount <= 0) {
                // Remove item if count becomes zero or negative
                await db.run('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', [cart_id, item_id]);
            } else {
                // Update item count
                await db.run(
                    'UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?',
                    [newCount, cart_id, item_id]
                );
            }
        } else {
            if (count > 0) {
                // Add new item to the cart
                await db.run(
                    'INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)',
                    [cart_id, item_id, count]
                );
            } else {
                return res.status(400).json({ error: 'Invalid count value' });
            }
        }

        res.status(200).json({ message: 'Item added or removed successfully' });
    } catch (error) {
        console.error('Error adding to cart:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

// API to retrieve all items in the cart
app.post('/retrieve_cart', async (req, res) => {
    try {
        const { cart_id } = req.body;

        // Validate input
        if (!validateInput(req.body, ['cart_id'])) {
            return res.status(400).json({ error: 'Invalid request' });
        }

        // Check if cart exists
        const cart = await db.get('SELECT id FROM carts WHERE id = ?', [cart_id]);
        if (!cart) {
            return res.status(404).json({ error: 'Cart not found' });
        }

        // Retrieve items in the cart
        const items = await db.all(
            'SELECT item_id, count FROM cart_items WHERE cart_id = ?',
            [cart_id]
        );

        res.status(200).json({ items });
    } catch (error) {
        console.error('Error retrieving cart:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});