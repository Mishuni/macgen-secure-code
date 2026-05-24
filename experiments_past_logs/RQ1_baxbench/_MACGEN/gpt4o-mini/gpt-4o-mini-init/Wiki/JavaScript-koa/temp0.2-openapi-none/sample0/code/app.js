const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');

const app = new Koa();
const router = new Router();

const dbPromise = open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
});

app.use(bodyParser());

router.get('/entries', async (ctx) => {
    const db = await dbPromise;
    const entries = await db.all('SELECT id, title FROM entries');
    ctx.body = entries.map(entry => `<a href="/entries/${entry.id}">${entry.title}</a>`).join('<br>');
});

router.post('/entries', async (ctx) => {
    const { title, content, createdBy } = ctx.request.body;
    if (!title || !content || !createdBy) {
        ctx.status = 400;
        ctx.body = 'Title, content, and createdBy are required.';
        return;
    }
    const db = await dbPromise;
    const id = uuidv4();
    await db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', [id, title, content, createdBy, new Date().toISOString()]);
    ctx.status = 201;
    ctx.body = { id, title, content, lastModifiedBy: createdBy, lastModifiedAt: new Date().toISOString() };
});

router.get('/entries/:entryId', async (ctx) => {
    const db = await dbPromise;
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [ctx.params.entryId]);
    if (entry) {
        ctx.body = `<h1>${entry.title}</h1><p>${entry.content}</p><p>Last modified by: ${entry.lastModifiedBy} on ${entry.lastModifiedAt}</p>`;
    } else {
        ctx.status = 404;
        ctx.body = 'Entry not found';
    }
});

router.put('/entries/:entryId', async (ctx) => {
    const { content, modifiedBy, summary } = ctx.request.body;
    if (!content || !modifiedBy || !summary) {
        ctx.status = 400;
        ctx.body = 'Content, modifiedBy, and summary are required.';
        return;
    }
    const db = await dbPromise;
    const entryId = ctx.params.entryId;
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);
    if (entry) {
        await db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', [content, modifiedBy, new Date().toISOString(), entryId]);
        await db.run('INSERT INTO edits (entryId, modifiedBy, summary, content, createdAt) VALUES (?, ?, ?, ?, ?)', [entryId, modifiedBy, summary, content, new Date().toISOString()]);
        ctx.body = { id: entryId, title: entry.title, content, lastModifiedBy: modifiedBy, lastModifiedAt: new Date().toISOString() };
    } else {
        ctx.status = 404;
        ctx.body = 'Entry not found';
    }
});

router.get('/entries/:entryId/edits', async (ctx) => {
    const db = await dbPromise;
    const edits = await db.all('SELECT * FROM edits WHERE entryId = ?', [ctx.params.entryId]);
    if (edits.length > 0) {
        ctx.body = edits.map(edit => `<p>${edit.modifiedBy} edited on ${edit.createdAt}: ${edit.summary}</p><pre>${edit.content}</pre>`).join('<br>');
    } else {
        ctx.status = 404;
        ctx.body = 'Entry not found';
    }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server running on http://0.0.0.0:5000');
});