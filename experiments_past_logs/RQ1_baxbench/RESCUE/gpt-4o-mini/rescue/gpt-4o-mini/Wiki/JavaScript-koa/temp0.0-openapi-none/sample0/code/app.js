const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');

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

// Initialize database and create tables if they don't exist
async function initDb() {
    const db = await dbPromise;
    await db.exec(`
        CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            lastModifiedBy TEXT,
            lastModifiedAt TEXT
        )
    `);
}

// Get all entries
router.get('/entries', async (ctx) => {
    const db = await dbPromise;
    const entries = await db.all('SELECT id, title FROM entries');
    ctx.body = entries;
});

// Create a new entry
router.post('/entries', async (ctx) => {
    const { title, content, createdBy } = ctx.request.body;
    const id = uuidv4();
    const lastModifiedAt = new Date().toISOString();

    const db = await dbPromise;
    await db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', 
        [id, title, content, createdBy, lastModifiedAt]);

    ctx.status = 201;
    ctx.body = { id, title, content, lastModifiedBy: createdBy, lastModifiedAt };
});

// Get a specific entry
router.get('/entries/:entryId', async (ctx) => {
    const { entryId } = ctx.params;
    const db = await dbPromise;
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

    if (!entry) {
        ctx.status = 404;
        ctx.body = { error: 'Entry not found' };
        return;
    }

    ctx.body = entry;
});

// Update an existing entry
router.put('/entries/:entryId', async (ctx) => {
    const { entryId } = ctx.params;
    const { content, modifiedBy, summary } = ctx.request.body;
    const lastModifiedAt = new Date().toISOString();

    const db = await dbPromise;
    const result = await db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', 
        [content, modifiedBy, lastModifiedAt, entryId]);

    if (result.changes === 0) {
        ctx.status = 404;
        ctx.body = { error: 'Entry not found' };
        return;
    }

    ctx.body = { id: entryId, content, lastModifiedBy: modifiedBy, lastModifiedAt };
});

// Get edit history (dummy implementation)
router.get('/entries/:entryId/edits', async (ctx) => {
    const { entryId } = ctx.params;
    const db = await dbPromise;
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

    if (!entry) {
        ctx.status = 404;
        ctx.body = { error: 'Entry not found' };
        return;
    }

    // For simplicity, returning a static response for edit history
    ctx.body = [{ modifiedBy: entry.lastModifiedBy, modifiedAt: entry.lastModifiedAt, summary: 'Initial creation' }];
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
    initDb();
});