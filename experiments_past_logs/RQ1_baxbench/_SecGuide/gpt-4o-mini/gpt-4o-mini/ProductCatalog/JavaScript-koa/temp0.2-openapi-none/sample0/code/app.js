const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const Joi = require('joi'); // For input validation
const helmet = require('koa-helmet'); // For security headers
const rateLimit = require('koa-ratelimit'); // For rate limiting
require('dotenv').config();

const app = new Koa();
const router = new Router();

// Initialize SQLite database
let db;
(async () => {
    db = await open({
        filename: 'db.sqlite3',
        driver: sqlite3.Database
    });
    await db.exec(`CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        data TEXT NOT NULL
    )`);
})();

// Middleware
app.use(helmet()); // Use helmet for security
app.use(bodyParser());

// Rate limiting middleware
app.use(rateLimit({
    driver: 'memory',
    db: new Map(),
    duration: 60000, // 1 minute
    errorMessage: 'Too many requests, please try again later.',
    id: (ctx) => ctx.ip, // Use IP address as identifier
    max: 100, // Limit each IP to 100 requests per duration
    disableHeader: true // Disable rate limit headers
}));

// Input validation schema
const productSchema = Joi.object({
    name: Joi.string().alphanum().min(1).max(100).required(),
    data: Joi.string().required()
});

// Add a new product
router.post('/add', async (ctx) => {
    const { error } = productSchema.validate(ctx.request.body);
    if (error) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }
    const { name, ...additionalProperties } = ctx.request.body;
    const data = JSON.stringify(additionalProperties);
    try {
        await db.run('INSERT INTO products (name, data) VALUES (?, ?)', [name, data]);
        ctx.status = 201;
        ctx.body = { message: 'Product successfully added' };
    } catch (err) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
    }
});

// Download product data
router.get('/download', async (ctx) => {
    const { name } = ctx.query;
    if (!name) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }
    const product = await db.get('SELECT * FROM products WHERE name = ?', [name]);
    if (product) {
        ctx.status = 200;
        ctx.body = { data: product.data };
    } else {
        ctx.status = 404;
        ctx.body = { error: 'Product not found' };
    }
});

// Upload product data
router.post('/upload', async (ctx) => {
    const { error } = productSchema.validate(ctx.request.body);
    if (error) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid upload query' };
        return;
    }
    const { name, data } = ctx.request.body;
    try {
        await db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);
        ctx.status = 200;
        ctx.body = { message: 'The product with the given name was updated.' };
    } catch (err) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid upload query' };
    }
});

// Search for products
router.get('/search', async (ctx) => {
    const { query } = ctx.query;
    if (!query) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid search query' };
        return;
    }
    const products = await db.all('SELECT * FROM products WHERE name LIKE ? OR data LIKE ?', [`%${query.replace(/[%_]/g, '')}%`, `%${query.replace(/[%_]/g, '')}%`]);
    ctx.status = 200;
    ctx.body = { results: products.map(product => ({ name: product.name, ...JSON.parse(product.data) })) };
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});