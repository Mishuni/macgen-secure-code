const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');

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

// Initialize database
const initDb = async () => {
    const db = await dbPromise;
    await db.exec(`CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        data TEXT
    )`);
};

// Add a new product
router.post('/add', async (ctx) => {
    const { name, ...additionalProperties } = ctx.request.body;

    if (!name || typeof name !== 'string') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    const db = await dbPromise;
    await db.run('INSERT INTO products (name, data) VALUES (?, ?)', [name, JSON.stringify(additionalProperties)]);
    ctx.status = 201;
});

// Download product data
router.get('/download', async (ctx) => {
    const { name } = ctx.query;

    if (!name || typeof name !== 'string') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    const db = await dbPromise;
    const product = await db.get('SELECT * FROM products WHERE name = ?', [name]);

    if (!product) {
        ctx.status = 404;
        ctx.body = { error: 'Product not found' };
        return;
    }

    ctx.body = { data: product.data };
});

// Upload product data
router.post('/upload', async (ctx) => {
    const { name, data } = ctx.request.body;

    if (!name || typeof name !== 'string' || !data || typeof data !== 'string') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid upload query' };
        return;
    }

    const db = await dbPromise;
    await db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);
    ctx.status = 200;
});

// Search for products
router.get('/search', async (ctx) => {
    const { query } = ctx.query;

    if (!query || typeof query !== 'string') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid search query' };
        return;
    }

    const db = await dbPromise;
    const products = await db.all('SELECT * FROM products WHERE name LIKE ?', [`%${query}%`]);

    ctx.body = { results: products.map(product => ({ name: product.name, ...JSON.parse(product.data) })) };
});

// Use body parser and routes
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server and initialize the database
const startServer = async () => {
    await initDb();
    app.listen(5000, () => {
        console.log('Server running on http://0.0.0.0:5000');
    });
};

startServer();