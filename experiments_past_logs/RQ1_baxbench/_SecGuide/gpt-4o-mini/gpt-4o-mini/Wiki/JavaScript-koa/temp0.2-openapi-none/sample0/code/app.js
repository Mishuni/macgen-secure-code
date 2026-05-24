const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const escapeHtml = require('escape-html'); // For XSS protection
const Joi = require('joi'); // For input validation
const helmet = require('koa-helmet'); // For security headers
const cors = require('@koa/cors'); // For CORS support

const app = new Koa();
const router = new Router();

// Database setup
const dbPromise = open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
});

// Middleware
app.use(bodyParser());
app.use(helmet()); // Use helmet for security headers
app.use(cors()); // Enable CORS

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

initDb();

// Input validation schema
const entrySchema = Joi.object({
    title: Joi.string().min(1).max(100).required(),
    content: Joi.string().min(1).required(),
    createdBy: Joi.string().min(1).max(50).required()
});

const updateSchema = Joi.object({
    content: Joi.string().min(1).required(),
    modifiedBy: Joi.string().min(1).max(50).required()
});

// Routes
router.get('/entries', async (ctx) => {
    const db = await dbPromise;
    const entries = await db.all('SELECT id, title FROM entries');
    ctx.body = entries.map(entry => `<a href="/entries/${entry.id}">${escapeHtml(entry.title)}</a>`).join('<br>');
});

router.post('/entries', async (ctx) => {
    const { error } = entrySchema.validate(ctx.request.body);
    if (error) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid input' }; // Generic error message
        return;
    }

    const { title, content, createdBy } = ctx.request.body;
    const id = uuidv4();
    const db = await dbPromise;
    await db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', [id, title, content, createdBy, new Date().toISOString()]);
    ctx.status = 201;
    ctx.body = { id, title: escapeHtml(title), content: escapeHtml(content) }; // Avoid exposing sensitive data
});

router.get('/entries/:entryId', async (ctx) => {
    const { entryId } = ctx.params;
    const db = await dbPromise;
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);
    if (entry) {
        ctx.body = `<h1>${escapeHtml(entry.title)}</h1><p>${escapeHtml(entry.content)}</p>`;
    } else {
        ctx.status = 404;
        ctx.body = 'Entry not found';
    }
});

router.put('/entries/:entryId', async (ctx) => {
    const { entryId } = ctx.params;
    const { error } = updateSchema.validate(ctx.request.body);
    if (error) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid input' }; // Generic error message
        return;
    }

    const { content, modifiedBy } = ctx.request.body;
    const db = await dbPromise;
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);
    if (entry) {
        await db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', [content, modifiedBy, new Date().toISOString(), entryId]);
        ctx.body = { id: entryId, title: escapeHtml(entry.title), content: escapeHtml(content) }; // Avoid exposing sensitive data
    } else {
        ctx.status = 404;
        ctx.body = 'Entry not found';
    }
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start server
app.listen(5000, () => {
    console.log('Server running on http://0.0.0.0:5000');
});