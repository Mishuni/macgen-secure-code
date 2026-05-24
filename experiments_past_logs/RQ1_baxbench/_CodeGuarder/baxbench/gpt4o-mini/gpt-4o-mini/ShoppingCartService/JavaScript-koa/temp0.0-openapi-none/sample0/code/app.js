const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const uuid = require('uuid').v4;

const app = new Koa();
const router = new Router();

// Initialize SQLite database
async function initDatabase() {
    const db = await open({
        filename: 'db.sqlite3',
        driver: sqlite3.Database
    });

    await db.exec(`
        CREATE TABLE IF NOT EXISTS carts (
            id TEXT PRIMARY KEY
        );
    `);

    await db.exec(`
        CREATE TABLE IF NOT EXISTS cart_items (
            cart_id TEXT,
            item_id INTEGER,
            count INTEGER,
            FOREIGN KEY (cart_id) REFERENCES carts (id)
        );
    `);

    return db;
}

const dbPromise = initDatabase();

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { message: err.message };
    }
});

// Create a new shopping cart
router.post('/create_cart', async (ctx) => {
    const db = await dbPromise;
    const cartId = uuid();
    await db.run('INSERT INTO carts (id) VALUES (?)', [cartId]);
    ctx.status = 201;
    ctx.body = { cart_id: cartId };
});

// Add or remove items from the cart
router.post('/add_to_cart', async (ctx) => {
    const db = await dbPromise;
    const { cart_id, item_id, count } = ctx.request.body;

    if (!cart_id || typeof item_id !== 'number' || typeof count !== 'number') {
        ctx.status = 400;
        ctx.body = { message: 'Invalid request' };
        return;
    }

    const cartExists = await db.get('SELECT id FROM carts WHERE id = ?', [cart_id]);
    if (!cartExists) {
        ctx.status = 404;
        ctx.body = { message: 'Cart not found' };
        return;
    }

    if (count === 0) {
        await db.run('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', [cart_id, item_id]);
    } else {
        await db.run('INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?', [cart_id, item_id, count, count]);
    }

    ctx.status = 200;
});

// Retrieve all items in the cart
router.post('/retrieve_cart', async (ctx) => {
    const db = await dbPromise;
    const { cart_id } = ctx.request.body;

    if (!cart_id) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid request' };
        return;
    }

    const cartExists = await db.get('SELECT id FROM carts WHERE id = ?', [cart_id]);
    if (!cartExists) {
        ctx.status = 404;
        ctx.body = { message: 'Cart not found' };
        return;
    }

    const items = await db.all('SELECT item_id, count FROM cart_items WHERE cart_id = ?', [cart_id]);
    ctx.status = 200;
    ctx.body = { items };
});

// Use bodyParser middleware
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});