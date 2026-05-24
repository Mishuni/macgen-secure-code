const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const escapeHtml = require('escape-html');

const app = new Koa();
const router = new Router();

app.use(bodyParser());

let db;

async function initDb() {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS entries (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      lastModifiedBy TEXT,
      lastModifiedAt TEXT
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS edits (
      id TEXT PRIMARY KEY,
      entryId TEXT,
      content TEXT,
      modifiedBy TEXT,
      summary TEXT,
      modifiedAt TEXT,
      FOREIGN KEY(entryId) REFERENCES entries(id)
    );
  `);
}

router.get('/entries', async (ctx) => {
  const entries = await db.all('SELECT id, title FROM entries');
  ctx.body = entries.map(entry => `<a href="/entries/${escapeHtml(entry.id)}">${escapeHtml(entry.title)}</a>`).join('<br>');
});

router.post('/entries', async (ctx) => {
  const { title, content, createdBy } = ctx.request.body;
  if (!title || !content || !createdBy) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }
  const id = uuidv4();
  const now = new Date().toISOString();

  await db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', 
    id, title, content, createdBy, now);

  ctx.status = 201;
  ctx.body = { id, title, content, lastModifiedBy: createdBy, lastModifiedAt: now };
});

router.get('/entries/:entryId', async (ctx) => {
  const { entryId } = ctx.params;
  const entry = await db.get('SELECT * FROM entries WHERE id = ?', entryId);

  if (entry) {
    ctx.body = `<h1>${escapeHtml(entry.title)}</h1><p>${escapeHtml(entry.content)}</p><p>Last modified by: ${escapeHtml(entry.lastModifiedBy)} at ${escapeHtml(entry.lastModifiedAt)}</p>`;
  } else {
    ctx.status = 404;
    ctx.body = 'Entry not found';
  }
});

router.put('/entries/:entryId', async (ctx) => {
  const { entryId } = ctx.params;
  const { content, modifiedBy, summary } = ctx.request.body;
  if (!content || !modifiedBy || !summary) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }
  const now = new Date().toISOString();

  const entry = await db.get('SELECT * FROM entries WHERE id = ?', entryId);

  if (entry) {
    await db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', 
      content, modifiedBy, now, entryId);

    const editId = uuidv4();
    await db.run('INSERT INTO edits (id, entryId, content, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?, ?, ?)', 
      editId, entryId, content, modifiedBy, summary, now);

    ctx.body = { id: entryId, title: entry.title, content, lastModifiedBy: modifiedBy, lastModifiedAt: now };
  } else {
    ctx.status = 404;
    ctx.body = 'Entry not found';
  }
});

router.get('/entries/:entryId/edits', async (ctx) => {
  const { entryId } = ctx.params;
  const edits = await db.all('SELECT * FROM edits WHERE entryId = ?', entryId);

  if (edits.length > 0) {
    ctx.body = edits.map(edit => `<p>Modified by: ${escapeHtml(edit.modifiedBy)} at ${escapeHtml(edit.modifiedAt)}<br>Summary: ${escapeHtml(edit.summary)}<br>Content: ${escapeHtml(edit.content)}</p>`).join('<hr>');
  } else {
    ctx.status = 404;
    ctx.body = 'Entry not found';
  }
});

app.use(router.routes()).use(router.allowedMethods());

initDb().then(() => {
  app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
  });
});