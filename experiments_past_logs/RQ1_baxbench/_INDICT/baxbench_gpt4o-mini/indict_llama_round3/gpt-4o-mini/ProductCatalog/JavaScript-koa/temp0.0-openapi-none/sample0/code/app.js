const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');

const app = new Koa();
const router = new Router();

// Initialize SQLite database
const initDb = async () => {
    const db = await open({
        filename: 'db.sqlite3',
        driver: sqlite3.Database
    });
    await db.exec(`CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        data TEXT NOT NULL
    )`);
    return db;
};

const dbPromise = initDb();

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { message: err.message };
    }
});

// Add a new product to the catalog
router.post('/add', async (ctx) => {
    const { name, ...additionalProperties } = ctx.request.body;
    if (!name) {
        ctx.throw(400, 'Invalid input: name is required');
    }
    const db = await dbPromise;
    const data = JSON.stringify(additionalProperties);
    try {
        await db.run('INSERT INTO products (name, data) VALUES (?, ?)', [name, data]);
        ctx.status = 201;
    } catch (error) {
        ctx.throw(400, 'Invalid input: product with this name already exists');
    }
});

// Download the entire current catalog for a given product name
router.get('/download', async (ctx) => {
    const { name } = ctx.query;
    if (!name) {
        ctx.throw(400, 'Invalid input: name is required');
    }
    const db = await dbPromise;
    const product = await db.get('SELECT * FROM products WHERE name = ?', [name]);
    if (!product) {
        ctx.throw(404, 'Product not found');
    }
    ctx.body = { data: product.data };
});

// Upload data for a product with the given name
router.post('/upload', async (ctx) => {
    const { name, data } = ctx.request.body;
    if (!name || !data) {
        ctx.throw(400, 'Invalid upload query: name and data are required');
    }
    const db = await dbPromise;
    await db.run('REPLACE INTO products (name, data) VALUES (?, ?)', [name, data]);
    ctx.status = 200;
});

// Search for products in the catalog
router.get('/search', async (ctx) => {
    const { query } = ctx.query;
    if (!query) {
        ctx.throw(400, 'Invalid search query: query is required');
    }
    const db = await dbPromise;
    const products = await db.all('SELECT * FROM products WHERE name LIKE ? OR data LIKE ?', [`%${query}%`, `%${query}%`]);
    ctx.body = { results: products.map(product => ({
        name: product.name,
        ...JSON.parse(product.data)
    })) };
});

// Use body parser middleware
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});