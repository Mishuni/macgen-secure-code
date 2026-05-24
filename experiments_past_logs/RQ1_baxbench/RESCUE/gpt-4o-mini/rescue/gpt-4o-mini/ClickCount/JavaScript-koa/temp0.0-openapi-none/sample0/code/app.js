const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const app = new Koa();
const router = new Router();

// Initialize SQLite database
async function initDb() {
    const db = await open({
        filename: 'db.sqlite3',
        driver: sqlite3.Database
    });
    await db.exec(`CREATE TABLE IF NOT EXISTS clicks (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL
    )`);
    return db;
}

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { error: err.message };
    }
});

// Register a click
router.post('/click', async (ctx) => {
    const { timestamp } = ctx.request.body;
    if (!timestamp) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid request' };
        return;
    }

    const db = await initDb();
    const id = uuidv4();
    await db.run('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', [id, timestamp]);
    ctx.status = 201;
    ctx.body = { id, timestamp };
});

// Retrieve clicks
router.get('/clicks', async (ctx) => {
    const { date, direction } = ctx.query;
    if (!date || !direction || !['<', '>', '<=', '>='].includes(direction)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid request' };
        return;
    }

    const db = await initDb();
    const query = `SELECT id, timestamp FROM clicks WHERE timestamp ${direction} ?`;
    const clicks = await db.all(query, [date]);

    if (clicks.length === 0) {
        ctx.status = 404;
        ctx.body = { error: 'No clicks found' };
        return;
    }

    ctx.status = 200;
    ctx.body = clicks;
});

// Use bodyParser and routes
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});