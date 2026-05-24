const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const uuid = require('uuid').v4;

const app = new Koa();
const router = new Router();

// Initialize SQLite database
const initDb = async () => {
    const db = await open({
        filename: 'db.sqlite3',
        driver: sqlite3.Database
    });
    await db.exec(`
        CREATE TABLE IF NOT EXISTS carts (
            id TEXT PRIMARY KEY,
            items TEXT
        )
    `);
    return db;
};

const dbPromise = initDb();

// Middleware to handle JSON responses
app.use(bodyParser());

// Function to validate item_id and count
const validateItem = (item_id, count) => {
    const itemIdRegex = /^[a-zA-Z0-9_-]{1,50}$/; // Example regex for item_id
    return itemIdRegex.test(item_id) && Number.isInteger(count) && count >= 0;
};

// Create a new shopping cart
router.post('/create_cart', async (ctx) => {
    const db = await dbPromise;
    const cartId = uuid();
    await db.run('INSERT INTO carts (id, items) VALUES (?, ?)', [cartId, JSON.stringify([])]);
    ctx.status = 201;
    ctx.body = { cart_id: cartId };
});

// Add or remove items from the cart
router.post('/add_to_cart', async (ctx) => {
    const db = await dbPromise;
    const { cart_id, item_id, count } = ctx.request.body;

    if (!cart_id || !item_id || count === undefined || !validateItem(item_id, count)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid request' };
        return;
    }

    const cart = await db.get('SELECT * FROM carts WHERE id = ?', [cart_id]);
    if (!cart) {
        ctx.status = 404;
        ctx.body = { error: 'Cart not found' };
        return;
    }

    const items = JSON.parse(cart.items);
    const existingItem = items.find(item => item.item_id === item_id);
    if (existingItem) {
        existingItem.count += count;
        if (existingItem.count <= 0) {
            items.splice(items.indexOf(existingItem), 1);
        }
    } else if (count > 0) {
        items.push({ item_id, count });
    }

    await db.run('UPDATE carts SET items = ? WHERE id = ?', [JSON.stringify(items), cart_id]);
    ctx.status = 200;
});

// Retrieve all items in the cart
router.post('/retrieve_cart', async (ctx) => {
    const db = await dbPromise;
    const { cart_id } = ctx.request.body;

    if (!cart_id) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid request' };
        return;
    }

    const cart = await db.get('SELECT * FROM carts WHERE id = ?', [cart_id]);
    if (!cart) {
        ctx.status = 404;
        ctx.body = { error: 'Cart not found' };
        return;
    }

    const items = JSON.parse(cart.items);
    ctx.status = 200;
    ctx.body = { items };
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});