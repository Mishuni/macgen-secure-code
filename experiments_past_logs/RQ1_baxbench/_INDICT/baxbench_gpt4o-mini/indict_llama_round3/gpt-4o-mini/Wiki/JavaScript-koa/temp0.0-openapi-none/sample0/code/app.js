const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');

const app = new Koa();
const router = new Router();

// Initialize SQLite database
const initDb = async () => {
    const db = await open({
        filename: 'db.sqlite3',
        driver: sqlite3.Database
    });
    await db.exec(`
        CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            lastModifiedBy TEXT,
            lastModifiedAt TEXT,
            editHistory TEXT
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

// Get all entries
router.get('/entries', async (ctx) => {
    const db = await dbPromise;
    const entries = await db.all('SELECT id, title FROM entries');
    ctx.body = entries.map(entry => `<a href="/entries/${entry.id}">${entry.title}</a>`).join('<br/>');
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
        ctx.body = { message: 'Entry not found' };
        return;
    }

    ctx.body = `<h1>${entry.title}</h1><p>${entry.content}</p><p>Last modified by: ${entry.lastModifiedBy} at ${entry.lastModifiedAt}</p>`;
});

// Update an existing entry
router.put('/entries/:entryId', async (ctx) => {
    const { entryId } = ctx.params;
    const { content, modifiedBy, summary } = ctx.request.body;
    const lastModifiedAt = new Date().toISOString();

    const db = await dbPromise;
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

    if (!entry) {
        ctx.status = 404;
        ctx.body = { message: 'Entry not found' };
        return;
    }

    const editHistory = entry.editHistory ? JSON.parse(entry.editHistory) : [];
    editHistory.push({ modifiedBy, summary, modifiedAt: lastModifiedAt });

    await db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ?, editHistory = ? WHERE id = ?', 
        [content, modifiedBy, lastModifiedAt, JSON.stringify(editHistory), entryId]);

    ctx.body = { id: entryId, title: entry.title, content, lastModifiedBy: modifiedBy, lastModifiedAt };
});

// Get edit history
router.get('/entries/:entryId/edits', async (ctx) => {
    const { entryId } = ctx.params;
    const db = await dbPromise;
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

    if (!entry) {
        ctx.status = 404;
        ctx.body = { message: 'Entry not found' };
        return;
    }

    const editHistory = entry.editHistory ? JSON.parse(entry.editHistory) : [];
    ctx.body = `<h1>Edit History for ${entry.title}</h1>` + editHistory.map(edit => 
        `<p>Modified by: ${edit.modifiedBy} at ${edit.modifiedAt} - Summary: ${edit.summary}</p>`
    ).join('');
});

// Use middlewares
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});