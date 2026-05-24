const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const dotenv = require('dotenv');
const bodyParser = require('body-parser');

dotenv.config();

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());

// Initialize SQLite database
let db;
(async () => {
    db = await sqlite.open({
        filename: 'db.sqlite3',
        driver: sqlite3.Database
    });

    // Create the products table if it doesn't exist
    await db.run(`
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            data TEXT NOT NULL
        )
    `);
})();

// Helper function to validate input
function isValidString(input) {
    return typeof input === 'string' && input.trim().length > 0;
}

// Route to add a new product
app.post('/add', async (req, res) => {
    try {
        const { name, ...properties } = req.body;

        if (!isValidString(name)) {
            return res.status(400).json({ error: 'Invalid product name' });
        }

        const id = require('uuid').v4();
        const data = JSON.stringify(properties);

        await db.run('INSERT INTO products (id, name, data) VALUES (?, ?, ?)', [id, name, data]);

        res.status(201).json({ message: 'Product successfully added' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Route to download product data by name
app.get('/download', async (req, res) => {
    try {
        const { name } = req.query;

        if (!isValidString(name)) {
            return res.status(400).json({ error: 'Invalid product name' });
        }

        const product = await db.get('SELECT data FROM products WHERE name = ?', [name]);

        if (!product) {
            return res.status(404).json({ error: 'Product not found' });
        }

        res.status(200).json({ data: product.data });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Route to upload product data by name
app.post('/upload', async (req, res) => {
    try {
        const { name, data } = req.body;

        if (!isValidString(name) || !isValidString(data)) {
            return res.status(400).json({ error: 'Invalid input' });
        }

        const result = await db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);

        if (result.changes === 0) {
            return res.status(404).json({ error: 'Product not found' });
        }

        res.status(200).json({ message: 'Product successfully updated' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Route to search for products
app.get('/search', async (req, res) => {
    try {
        const { query } = req.query;

        if (!isValidString(query)) {
            return res.status(400).json({ error: 'Invalid search query' });
        }

        const products = await db.all(`
            SELECT name, data FROM products
            WHERE name LIKE ? OR data LIKE ?
        `, [`%${query}%`, `%${query}%`]);

        const results = products.map(product => ({
            name: product.name,
            ...JSON.parse(product.data)
        }));

        res.status(200).json({ results });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});