const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');
const cors = require('@koa/cors');
const DOMPurify = require('dompurify');

const app = new Koa();
const router = new Router();
const dbPath = path.join(__dirname, 'db.sqlite3');

// Initialize SQLite database
const db = new sqlite3.Database(dbPath, (err) => {
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

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { message: 'Internal Server Error' };
        console.error(err); // Log error details for debugging
    }
});

// Enable CORS with specific origin
app.use(cors({
    origin: 'http://your-allowed-origin.com' // Replace with your allowed origin
}));

// Input validation function
const validateInput = (product_name, tags) => {
    if (typeof product_name !== 'string' || product_name.length > 100) {
        return false;
    }
    if (!Array.isArray(tags) || tags.length > 10 || !tags.every(tag => typeof tag === 'string' && tag.length <= 30)) {
        return false;
    }
    return true;
};

// Get all posted products that match at least one of the provided tags
router.get('/recommender', async (ctx) => {
    const tags = ctx.query.tags;
    if (!tags) {
        ctx.throw(400, 'Tags are required');
    }

    const tagArray = tags.split(',').map(tag => tag.trim());
    const products = [];

    for (const tag of tagArray) {
        const sanitizedTag = tag.replace(/[%_]/g, ''); // Sanitize tag to prevent SQL injection
        const sql = `SELECT * FROM products WHERE tags LIKE ?`;
        const rows = await new Promise((resolve, reject) => {
            db.all(sql, [`%${sanitizedTag}%`], (err, rows) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(rows);
                }
            });
        });
        products.push(...rows);
    }

    ctx.type = 'text/html';
    ctx.body = `<html><body><h1>Recommended Products</h1><ul>${products.map(product => `<li>${DOMPurify.sanitize(product.product_name)} - Tags: ${DOMPurify.sanitize(product.tags)}</li>`).join('')}</ul></body></html>`;
});

// Post a new product along with its tags
router.post('/recommender', async (ctx) => {
    const { product_name, tags } = ctx.request.body;

    if (!validateInput(product_name, tags)) {
        ctx.throw(400, 'Invalid input');
    }

    const tagsString = tags.join(',');
    const sql = `INSERT INTO products (product_name, tags) VALUES (?, ?)`;
    await new Promise((resolve, reject) => {
        db.run(sql, [product_name, tagsString], function (err) {
            if (err) {
                reject(err);
            } else {
                resolve(this.lastID);
            }
        });
    });

    ctx.status = 200;
    ctx.body = { message: 'Product added successfully' };
});

// Use bodyParser middleware
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});