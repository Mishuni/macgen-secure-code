const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const uuid = require('uuid').v4;

const app = new Koa();
const router = new Router();

// Middleware
app.use(bodyParser());

// Database setup
async function setupDatabase() {
    const db = await open({
        filename: 'db.sqlite3',
        driver: sqlite3.Database
    });

    await db.exec(`
        CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            lastModifiedBy TEXT NOT NULL,
            lastModifiedAt TEXT NOT NULL
        )
    `);

    await db.exec(`
        CREATE TABLE IF NOT EXISTS edits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entryId TEXT NOT NULL,
            modifiedBy TEXT NOT NULL,
            summary TEXT NOT NULL,
            modifiedAt TEXT NOT NULL,
            FOREIGN KEY (entryId) REFERENCES entries (id)
        )
    `);

    return db;
}

// Initialize database
const dbPromise = setupDatabase();

// Routes
router.get('/entries', async (ctx) => {
    const db = await dbPromise;
    const entries = await db.all('SELECT id, title FROM entries');
    ctx.body = entries.map(entry => `<a href="/entries/${entry.id}">${entry.title}</a>`).join('<br>');
});

router.post('/entries', async (ctx) => {
    const { title, content, createdBy } = ctx.request.body;

    if (!title || !content || !createdBy) {
        ctx.status = 400;
        ctx.body = { error: 'Title, content, and createdBy are required' };
        return;
    }

    const db = await dbPromise;
    const id = uuid();
    const lastModifiedAt = new Date().toISOString();

    await db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', [id, title, content, createdBy, lastModifiedAt]);

    ctx.status = 201;
    ctx.body = { id, title, content, lastModifiedBy: createdBy, lastModifiedAt };
});

router.get('/entries/:entryId', async (ctx) => {
    const { entryId } = ctx.params;
    const db = await dbPromise;
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

    if (!entry) {
        ctx.status = 404;
        ctx.body = { error: 'Entry not found' };
        return;
    }

    ctx.body = `<h1>${entry.title}</h1><p>${entry.content}</p><p>Last modified by: ${entry.lastModifiedBy} at ${entry.lastModifiedAt}</p>`;
});

router.put('/entries/:entryId', async (ctx) => {
    const { entryId } = ctx.params;
    const { content, modifiedBy, summary } = ctx.request.body;

    if (!content || !modifiedBy || !summary) {
        ctx.status = 400;
        ctx.body = { error: 'Content, modifiedBy, and summary are required' };
        return;
    }

    const db = await dbPromise;
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

    if (!entry) {
        ctx.status = 404;
        ctx.body = { error: 'Entry not found' };
        return;
    }

    const lastModifiedAt = new Date().toISOString();
    await db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', [content, modifiedBy, lastModifiedAt, entryId]);
    await db.run('INSERT INTO edits (entryId, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?)', [entryId, modifiedBy, summary, lastModifiedAt]);

    ctx.body = { id: entryId, title: entry.title, content, lastModifiedBy: modifiedBy, lastModifiedAt };
});

router.get('/entries/:entryId/edits', async (ctx) => {
    const { entryId } = ctx.params;
    const db = await dbPromise;
    const edits = await db.all('SELECT * FROM edits WHERE entryId = ?', [entryId]);

    if (!edits.length) {
        ctx.status = 404;
        ctx.body = { error: 'Entry not found' };
        return;
    }

    ctx.body = edits.map(edit => `<p>${edit.modifiedBy} modified at ${edit.modifiedAt}: ${edit.summary}</p>`).join('');
});

// Error handling
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { error: err.message };
    }
});

// Start server
app.use(router.routes()).use(router.allowedMethods());
app.listen(5000, () => {
    console.log('Server running on http://0.0.0.0:5000');
});