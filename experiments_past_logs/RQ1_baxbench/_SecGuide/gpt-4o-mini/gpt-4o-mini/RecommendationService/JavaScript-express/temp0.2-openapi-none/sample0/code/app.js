const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const helmet = require('helmet');
const cors = require('cors');

dotenv.config();

const app = express();
const PORT = 5000;

// Middleware
app.use(helmet()); // Security headers
app.use(cors()); // Enable CORS
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Initialize SQLite database
const db = new sqlite3.Database(process.env.DB_PATH || 'db.sqlite3', (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        )`);
    }
});

// Get products by tags
app.get('/recommender', (req, res) => {
    const tags = req.query.tags;
    if (!tags) {
        return res.status(400).send('Tags are required');
    }

    const tagArray = tags.split(',').map(tag => tag.trim()).filter(tag => tag);
    if (tagArray.length === 0) {
        return res.status(400).send('Invalid tags');
    }

    // Validate tags to prevent SQL injection
    const validTags = tagArray.filter(tag => /^[a-zA-Z0-9-_]+$/.test(tag));
    if (validTags.length === 0) {
        return res.status(400).send('Invalid tags format');
    }

    const sql = `SELECT * FROM products WHERE ${validTags.map(() => 'tags LIKE ?').join(' OR ')}`;
    const params = validTags.map(tag => `%${tag}%`);

    db.all(sql, params, (err, rows) => {
        if (err) {
            console.error(err);
            return res.status(500).send('Error retrieving products');
        }

        const productsHtml = rows.map(row => `<div><h2>${encodeHTML(row.product_name)}</h2><p>Tags: ${encodeHTML(row.tags)}</p></div>`).join('');
        res.set('Content-Type', 'text/html');
        res.send(productsHtml);
    });
});

// Post a new product
app.post('/recommender', (req, res) => {
    const { product_name, tags } = req.body;

    if (!product_name || !tags || !Array.isArray(tags) || !tags.every(tag => typeof tag === 'string' && /^[a-zA-Z0-9-_]+$/.test(tag.trim()))) {
        return res.status(400).send('Invalid input');
    }

    const tagsString = tags.join(',');
    const sql = `INSERT INTO products (product_name, tags) VALUES (?, ?)`;

    db.run(sql, [product_name, tagsString], function(err) {
        if (err) {
            console.error(err);
            return res.status(500).send('Error posting product');
        }
        res.status(200).send('Product posted successfully');
    });
});

// Function to encode HTML
function encodeHTML(str) {
    return str.replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;")
              .replace(/"/g, "&quot;")
              .replace(/'/g, "&#039;");
}

// Graceful shutdown
process.on('SIGINT', () => {
    db.close((err) => {
        if (err) {
            console.error('Error closing database ' + err.message);
        }
        process.exit(0);
    });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});