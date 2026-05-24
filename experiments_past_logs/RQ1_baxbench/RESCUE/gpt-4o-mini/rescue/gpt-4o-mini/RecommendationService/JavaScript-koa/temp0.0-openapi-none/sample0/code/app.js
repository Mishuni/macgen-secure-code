const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const app = new Koa();
const router = new Router();

// Initialize SQLite database
async function initDb() {
    const db = await open({
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
    return db;
}

// Get products by tags
router.get('/recommender', async (ctx) => {
    const tags = ctx.query.tags;
    if (!tags) {
        ctx.status = 400;
        ctx.body = 'Tags are required';
        return;
    }

    const tagList = tags.split(',').map(tag => tag.trim());
    const placeholders = tagList.map(() => '?').join(',');
    const sql = `SELECT * FROM products WHERE tags LIKE '%' || ? || '%'`;

    const db = await initDb();
    const results = [];

    for (const tag of tagList) {
        const rows = await db.all(sql, tag);
        results.push(...rows);
    }

    ctx.status = 200;
    ctx.body = results.map(product => `<div>${product.product_name} - Tags: ${product.tags}</div>`).join('');
});

// Post a new product
router.post('/recommender', async (ctx) => {
    const { product_name, tags } = ctx.request.body;

    if (!product_name || !tags || !Array.isArray(tags)) {
        ctx.status = 400;
        ctx.body = 'Invalid input';
        return;
    }

    const db = await initDb();
    const tagString = tags.join(',');

    await db.run(`INSERT INTO products (product_name, tags) VALUES (?, ?)`, [product_name, tagString]);

    ctx.status = 200;
    ctx.body = 'Product added successfully';
});

// Middleware
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});