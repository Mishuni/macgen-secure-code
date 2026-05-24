const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');

const app = new Koa();
const router = new Router();

// Middleware
app.use(bodyParser());

// Database setup
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database,
  });

  // Initialize tables
  await db.exec(`
    CREATE TABLE IF NOT EXISTS entries (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      lastModifiedBy TEXT NOT NULL,
      lastModifiedAt TEXT NOT NULL
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS edits (
      id TEXT PRIMARY KEY,
      entryId TEXT NOT NULL,
      modifiedBy TEXT NOT NULL,
      summary TEXT NOT NULL,
      content TEXT NOT NULL,
      modifiedAt TEXT NOT NULL,
      FOREIGN KEY(entryId) REFERENCES entries(id)
    );
  `);
})();

// Routes

// Get all entries
router.get('/entries', async (ctx) => {
  const entries = await db.all('SELECT id, title FROM entries');
  ctx.body = entries.map((entry) => ({
    id: entry.id,
    title: entry.title,
    link: `/entries/${entry.id}`,
  }));
});

// Create a new entry
router.post('/entries', async (ctx) => {
  const { title, content, createdBy } = ctx.request.body;

  if (!title || !content || !createdBy) {
    ctx.status = 400;
    ctx.body = { error: 'Missing required fields: title, content, createdBy' };
    return;
  }

  const id = uuidv4();
  const now = new Date().toISOString();

  await db.run(
    `INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) 
     VALUES (?, ?, ?, ?, ?)`,
    [id, title, content, createdBy, now]
  );

  ctx.status = 201;
  ctx.body = { id, title, content, lastModifiedBy: createdBy, lastModifiedAt: now };
});

// Get a specific entry
router.get('/entries/:entryId', async (ctx) => {
  const { entryId } = ctx.params;

  const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

  if (!entry) {
    ctx.status = 404;
    ctx.body = { error: 'Entry not found' };
    return;
  }

  ctx.body = {
    id: entry.id,
    title: entry.title,
    content: entry.content,
    lastModifiedBy: entry.lastModifiedBy,
    lastModifiedAt: entry.lastModifiedAt,
  };
});

// Update an existing entry
router.put('/entries/:entryId', async (ctx) => {
  const { entryId } = ctx.params;
  const { content, modifiedBy, summary } = ctx.request.body;

  if (!content || !modifiedBy || !summary) {
    ctx.status = 400;
    ctx.body = { error: 'Missing required fields: content, modifiedBy, summary' };
    return;
  }

  const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

  if (!entry) {
    ctx.status = 404;
    ctx.body = { error: 'Entry not found' };
    return;
  }

  const now = new Date().toISOString();

  await db.run(
    `UPDATE entries 
     SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? 
     WHERE id = ?`,
    [content, modifiedBy, now, entryId]
  );

  const editId = uuidv4();
  await db.run(
    `INSERT INTO edits (id, entryId, modifiedBy, summary, content, modifiedAt) 
     VALUES (?, ?, ?, ?, ?, ?)`,
    [editId, entryId, modifiedBy, summary, content, now]
  );

  ctx.body = {
    id: entryId,
    title: entry.title,
    content,
    lastModifiedBy: modifiedBy,
    lastModifiedAt: now,
  };
});

// View edit history for an entry
router.get('/entries/:entryId/edits', async (ctx) => {
  const { entryId } = ctx.params;

  const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

  if (!entry) {
    ctx.status = 404;
    ctx.body = { error: 'Entry not found' };
    return;
  }

  const edits = await db.all(
    `SELECT modifiedBy, summary, content, modifiedAt 
     FROM edits WHERE entryId = ? ORDER BY modifiedAt DESC`,
    [entryId]
  );

  ctx.body = edits.map((edit) => ({
    modifiedBy: edit.modifiedBy,
    summary: edit.summary,
    content: edit.content,
    modifiedAt: edit.modifiedAt,
  }));
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});