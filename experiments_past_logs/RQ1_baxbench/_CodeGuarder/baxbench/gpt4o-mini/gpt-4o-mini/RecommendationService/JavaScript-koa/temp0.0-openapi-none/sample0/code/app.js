import Koa from 'koa';
import Router from 'koa-router';
import bodyParser from 'koa-bodyparser';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';

dotenv.config();

const app = new Koa();
const router = new Router();
const dbPromise = open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
});

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { error: err.message };
    }
});

// Middleware to parse JSON bodies
app.use(bodyParser());

// Initialize the database and create the products table if it doesn't exist
const initDb = async () => {
    const db = await dbPromise;
    await db.exec(`CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        tags TEXT NOT NULL
    )`);
};

// GET endpoint to retrieve products by tags
router.get('/recommender', async (ctx) => {
    const tags = ctx.query.tags;
    if (!tags) {
        ctx.status = 400;
        ctx.body = { error: 'Tags query parameter is required' };
        return;
    }

    const tagList = tags.split(',').map(tag => tag.trim());
    const db = await dbPromise;
    const products = await db.all(`SELECT * FROM products WHERE tags LIKE ?`, `%${tagList[0]}%`);

    ctx.status = 200;
    ctx.body = products.map(product => `<div><h2>${product.product_name}</h2><p>Tags: ${product.tags}</p></div>`).join('');
});

// POST endpoint to add a new product
router.post('/recommender', async (ctx) => {
    const { product_name, tags } = ctx.request.body;

    if (!product_name || !Array.isArray(tags) || tags.length === 0) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    const db = await dbPromise;
    await db.run(`INSERT INTO products (product_name, tags) VALUES (?, ?)`, product_name, tags.join(','));

    ctx.status = 200;
    ctx.body = { message: 'Product added successfully' };
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const startServer = async () => {
    await initDb();
    app.listen(5000, '0.0.0.0', () => {
        console.log('Server is running on http://0.0.0.0:5000');
    });
};

startServer();