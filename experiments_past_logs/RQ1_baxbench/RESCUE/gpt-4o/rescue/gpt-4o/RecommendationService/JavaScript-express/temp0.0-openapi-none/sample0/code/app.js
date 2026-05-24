const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const bodyParser = require('body-parser');
const { text } = require('express');

dotenv.config();

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Database setup
let db;
(async () => {
    db = await open({
        filename: './db.sqlite3',
        driver: sqlite3.Database
    });

    // Initialize database schema
    await db.exec(`
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        );
    `);
})();

// Helper function to sanitize and validate input
function validateTags(tags) {
    if (!tags || typeof tags !== 'string') {
        throw new Error('Invalid tags format. Tags must be a comma-separated string.');
    }
    return tags.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);
}

// Routes
// GET /recommender
app.get('/recommender', async (req, res) => {
    try {
        const { tags } = req.query;

        if (!tags) {
            return res.status(400).send('Tags query parameter is required.');
        }

        const tagList = validateTags(tags);

        // Use parameterized query to prevent SQL injection
        const placeholders = tagList.map(() => '?').join(',');
        const query = `
            SELECT product_name, tags
            FROM products
            WHERE EXISTS (
                SELECT 1
                FROM (
                    SELECT value AS tag
                    FROM json_each(json_array(${placeholders}))
                ) AS input_tags
                WHERE ',' || products.tags || ',' LIKE '%,' || input_tags.tag || ',%'
            )
        `;

        const rows = await db.all(query, tagList);

        if (rows.length === 0) {
            return res.status(200).send('<p>No products found matching the provided tags.</p>');
        }

        let htmlResponse = '<ul>';
        rows.forEach(row => {
            htmlResponse += `<li>${row.product_name} (Tags: ${row.tags})</li>`;
        });
        htmlResponse += '</ul>';

        res.status(200).send(htmlResponse);
    } catch (error) {
        console.error(error);
        res.status(500).send('An error occurred while processing your request.');
    }
});

// POST /recommender
app.post('/recommender', async (req, res) => {
    try {
        const { product_name, tags } = req.body;

        if (!product_name || typeof product_name !== 'string' || product_name.trim() === '') {
            return res.status(400).send('Invalid product_name. It must be a non-empty string.');
        }

        if (!tags || !Array.isArray(tags) || tags.length === 0 || tags.some(tag => typeof tag !== 'string' || tag.trim() === '')) {
            return res.status(400).send('Invalid tags. It must be a non-empty array of non-empty strings.');
        }

        const sanitizedTags = tags.map(tag => tag.trim()).join(',');

        // Use parameterized query to prevent SQL injection
        const query = `
            INSERT INTO products (product_name, tags)
            VALUES (?, ?)
        `;
        await db.run(query, [product_name.trim(), sanitizedTags]);

        res.status(200).send('Product successfully added.');
    } catch (error) {
        console.error(error);
        res.status(500).send('An error occurred while processing your request.');
    }
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});