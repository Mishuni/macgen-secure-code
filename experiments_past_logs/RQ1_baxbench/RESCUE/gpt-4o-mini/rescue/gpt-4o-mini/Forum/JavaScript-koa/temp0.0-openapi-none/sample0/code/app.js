const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const app = new Koa();
const router = new Router();

// Open SQLite database
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
        ctx.app.emit('error', err, ctx);
    }
});

// Body parser middleware
app.use(bodyParser());

// Initialize database and create messages table if it doesn't exist
dbPromise.then(db => {
    return db.exec(`CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        username TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);
});

// Get all messages
router.get('/messages', async (ctx) => {
    const limit = ctx.query.limit ? parseInt(ctx.query.limit) : 10;
    const offset = ctx.query.offset ? parseInt(ctx.query.offset) : 0;
    const sort = ctx.query.sort === 'ASC' ? 'ASC' : 'DESC';

    const db = await dbPromise;
    const messages = await db.all(`SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`, [limit, offset]);
    ctx.body = messages;
});

// Post a new message
router.post('/messages', async (ctx) => {
    const { content, username } = ctx.request.body;

    if (!content || !username) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    const db = await dbPromise;
    await db.run(`INSERT INTO messages (content, username) VALUES (?, ?)`, [content, username]);
    ctx.status = 200;
    ctx.body = { message: 'Message posted successfully' };
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});