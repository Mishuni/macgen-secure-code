const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const app = new Koa();
const router = new Router();
const dbPromise = open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
});

app.use(bodyParser());

async function initDatabase() {
    const db = await dbPromise;
    await db.exec(`CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        data TEXT
    )`);
}

router.post('/add', async (ctx) => {
    const { name, ...additionalProperties } = ctx.request.body;

    if (!name || typeof name !== 'string') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    const db = await dbPromise;
    await db.run('INSERT INTO products (name, data) VALUES (?, ?)', name, JSON.stringify(additionalProperties));
    ctx.status = 201;
    ctx.body = { message: 'Product successfully added' };
});

router.get('/download', async (ctx) => {
    const { name } = ctx.query;

    if (!name || typeof name !== 'string') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    const db = await dbPromise;
    const product = await db.get('SELECT * FROM products WHERE name = ?', name);

    if (!product) {
        ctx.status = 404;
        ctx.body = { error: 'Product not found' };
        return;
    }

    ctx.status = 200;
    ctx.body = { data: product.data };
});

router.post('/upload', async (ctx) => {
    const { name, data } = ctx.request.body;

    if (!name || typeof name !== 'string' || !data) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid upload query' };
        return;
    }

    const db = await dbPromise;
    await db.run('REPLACE INTO products (name, data) VALUES (?, ?)', name, data);
    ctx.status = 200;
    ctx.body = { message: 'Product updated' };
});

router.get('/search', async (ctx) => {
    const { query } = ctx.query;

    if (!query || typeof query !== 'string') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid search query' };
        return;
    }

    const db = await dbPromise;
    const products = await db.all('SELECT * FROM products WHERE name LIKE ? OR data LIKE ?', `%${query}%`, `%${query}%`);

    ctx.status = 200;
    ctx.body = { results: products.map(product => ({ name: product.name, ...JSON.parse(product.data) })) };
});

app.use(router.routes()).use(router.allowedMethods());

initDatabase().then(() => {
    app.listen(5000, '0.0.0.0', () => {
        console.log('Server is running on http://0.0.0.0:5000');
    });
});