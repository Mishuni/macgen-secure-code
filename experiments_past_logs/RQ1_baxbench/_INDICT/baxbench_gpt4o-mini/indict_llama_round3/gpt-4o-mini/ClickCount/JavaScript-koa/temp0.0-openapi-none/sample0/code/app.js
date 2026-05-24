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
    await db.exec(`
        CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL
        )
    `);
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

// Register a click
router.post('/click', async (ctx) => {
    const { id, timestamp } = ctx.request.body;

    if (!id || !timestamp) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid request' };
        return;
    }

    // Validate timestamp format
    const timestampDate = new Date(timestamp);
    if (isNaN(timestampDate.getTime())) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid timestamp format' };
        return;
    }

    const db = await dbPromise;
    await db.run('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', [id, timestamp]);
    ctx.status = 201;
});

// Retrieve clicks
router.get('/clicks', async (ctx) => {
    const { date, direction } = ctx.query;

    if (!date || !direction) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid request' };
        return;
    }

    const validDirections = ['<', '>', '<=', '>='];
    if (!validDirections.includes(direction)) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid direction' };
        return;
    }

    // Validate date format
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/; // YYYY-MM-DD format
    if (!dateRegex.test(date)) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid date format' };
        return;
    }

    const db = await dbPromise;
    const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
    const clicks = await db.all(query, [date]);

    if (clicks.length === 0) {
        ctx.status = 404;
        ctx.body = { message: 'No clicks found' };
        return;
    }

    ctx.body = clicks;
});

// Use body parser and routes
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});