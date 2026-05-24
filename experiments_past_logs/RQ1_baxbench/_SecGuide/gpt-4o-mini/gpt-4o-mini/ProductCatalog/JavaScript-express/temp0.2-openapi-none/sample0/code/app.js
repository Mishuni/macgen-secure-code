const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const { body, validationResult } = require('express-validator');
const cors = require('cors');

dotenv.config();

const app = express();
const PORT = 5000;

// Middleware
app.use(cors()); // Implement CORS policy
app.use(bodyParser.json());

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            data TEXT
        )`, (err) => {
            if (err) {
                console.error('Error creating table ' + err.message);
            }
        });
    }
});

// Validate input for adding a new product
const validateProductInput = [
    body('name').isString().isLength({ max: 100 }).withMessage('Name must be a string and less than 100 characters.'),
    body('data').optional().isJSON().withMessage('Data must be a valid JSON string.')
];

// Add a new product to the catalog
app.post('/add', validateProductInput, (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
    }
    
    const { name, ...additionalProperties } = req.body;
    const data = JSON.stringify(additionalProperties);
    db.run(`INSERT INTO products (name, data) VALUES (?, ?)`, [name, data], function(err) {
        if (err) {
            return res.status(400).json({ error: 'Invalid input' });
        }
        res.status(201).json({ id: this.lastID });
    });
});

// Download the entire current catalog for a given product name
app.get('/download', (req, res) => {
    const { name } = req.query;
    if (!name) {
        return res.status(400).json({ error: 'Invalid input' });
    }
    db.get(`SELECT data FROM products WHERE name = ?`, [name], (err, row) => {
        if (err || !row) {
            return res.status(404).json({ error: 'Product not found' });
        }
        res.json({ data: row.data });
    });
});

// Validate input for uploading data
const validateUploadInput = [
    body('name').isString().isLength({ max: 100 }).withMessage('Name must be a string and less than 100 characters.'),
    body('data').isString().isLength({ max: 10000 }).withMessage('Data must be a string and less than 10,000 characters.')
];

// Upload data for a product
app.post('/upload', validateUploadInput, (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
    }
    
    const { name, data } = req.body;
    db.run(`UPDATE products SET data = ? WHERE name = ?`, [data, name], function(err) {
        if (err || this.changes === 0) {
            return res.status(404).json({ error: 'Product not found or invalid upload' });
        }
        res.status(200).json({ message: 'Product updated' });
    });
});

// Validate input for searching products
const validateSearchInput = [
    body('query').isString().isLength({ max: 100 }).withMessage('Query must be a string and less than 100 characters.')
];

// Search for products in the catalog
app.get('/search', validateSearchInput, (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
    }
    
    const { query } = req.query;
    db.all(`SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?`, [`%${query}%`, `%${query}%`], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: 'Search error' });
        }
        res.json({ results: rows.map(row => ({ name: row.name, ...JSON.parse(row.data) })) });
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});