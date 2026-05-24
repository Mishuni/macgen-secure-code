const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const app = new Koa();
const router = new Router();

// Initialize SQLite database
let db;

const initDb = async () => {
    if (!db) {
        db = await open({
            filename: 'db.sqlite3',
            driver: sqlite3.Database
        });

        await db.exec(`
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                tags TEXT NOT NULL
            )
        `);
    }
};

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { error: err.message };
    }
});

// Get products by tags
router.get('/recommender', async (ctx) => {
    const tagsQuery = ctx.query.tags;
    if (!tagsQuery) {
        ctx.throw(400, 'Tags query parameter is required');
    }

    const tags = tagsQuery.split(',').map(tag => tag.trim());
    await initDb();

    const placeholders = tags.map(() => 'tags LIKE ?').join(' OR ');
    const sql = `SELECT * FROM products WHERE ${placeholders}`;
    const products = await db.all(sql, tags.map(tag => `%${tag}%`));

    ctx.body = products.map(product => `<div><h2>${product.product_name}</h2><p>Tags: ${product.tags}</p></div>`).join('');
    ctx.type = 'text/html';
});

// Post a new product
router.post('/recommender', async (ctx) => {
    const { product_name, tags } = ctx.request.body;

    if (!product_name || !Array.isArray(tags)) {
        ctx.throw(400, 'Invalid input');
    }

    await initDb();
    await db.run(`
        INSERT INTO products (product_name, tags) VALUES (?, ?)
    `, [product_name, tags.join(',')]);

    ctx.status = 200;
    ctx.body = { message: 'Product added successfully' };
});

// Use body parser and router
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});