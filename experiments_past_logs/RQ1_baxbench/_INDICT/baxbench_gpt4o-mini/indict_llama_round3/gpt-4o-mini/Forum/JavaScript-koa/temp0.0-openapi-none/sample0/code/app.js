const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const app = new Koa();
const router = new Router();

// Initialize SQLite database
let db;
const initDb = async () => {
    if (!db) {
        db = await open({
            filename: 'db.sqlite3',
            driver: sqlite3.Database
        });
        await db.exec(`
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                username TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);
    }
};

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { message: err.message };
        ctx.app.emit('error', err, ctx);
    }
});

// Get all messages
router.get('/messages', async (ctx) => {
    const limit = parseInt(ctx.query.limit) || 10;
    const offset = parseInt(ctx.query.offset) || 0;
    const sort = ctx.query.sort === 'ASC' ? 'ASC' : 'DESC';

    await initDb();
    const messages = await db.all(`SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`, [limit, offset]);
    ctx.body = messages;
});

// Post a new message
router.post('/messages', async (ctx) => {
    const { content, username } = ctx.request.body;

    if (typeof content !== 'string' || typeof username !== 'string' || content.trim() === '' || username.trim() === '') {
        ctx.throw(400, 'Invalid input');
    }

    await initDb();
    await db.run(`INSERT INTO messages (content, username) VALUES (?, ?)`, [content, username]);
    ctx.status = 200;
});

// Use body parser and router
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});