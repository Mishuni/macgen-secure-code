const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const helmet = require('koa-helmet');
const escapeHtml = require('escape-html');
const Joi = require('joi');

const app = new Koa();
const router = new Router();

let db;

// Initialize the database
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
    
    CREATE TABLE IF NOT EXISTS edits (
      id TEXT PRIMARY KEY,
      entryId TEXT,
      modifiedBy TEXT,
      summary TEXT,
      modifiedAt TEXT,
      FOREIGN KEY(entryId) REFERENCES entries(id)
    );
  `);
}

// Middleware for error handling
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = 'Internal Server Error';
    console.error(err);
  }
});

// Use helmet for setting HTTP security headers
app.use(helmet());

// Input validation schemas
const entrySchema = Joi.object({
  title: Joi.string().min(1).max(255).required(),
  content: Joi.string().min(1).required(),
  createdBy: Joi.string().min(1).max(255).required()
});

const updateSchema = Joi.object({
  content: Joi.string().min(1).required(),
  modifiedBy: Joi.string().min(1).max(255).required(),
  summary: Joi.string().min(1).max(255).required()
});

// Get all entries
router.get('/entries', async (ctx) => {
  const entries = await db.all('SELECT id, title FROM entries');
  ctx.type = 'text/html';
  ctx.body = entries.map(entry => `<a href="/entries/${entry.id}">${escapeHtml(entry.title)}</a>`).join('<br>');
});

// Create a new entry
router.post('/entries', async (ctx) => {
  const { error, value } = entrySchema.validate(ctx.request.body);
  if (error) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }
  const { title, content, createdBy } = value;
  const id = uuidv4();
  const now = new Date().toISOString();

  await db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', 
    id, title, content, createdBy, now);

  ctx.status = 201;
  ctx.body = { id, title, content, lastModifiedBy: createdBy, lastModifiedAt: now };
});

// Get a specific entry
router.get('/entries/:entryId', async (ctx) => {
  const { entryId } = ctx.params;
  const entry = await db.get('SELECT * FROM entries WHERE id = ?', entryId);

  if (entry) {
    ctx.type = 'text/html';
    ctx.body = `<h1>${escapeHtml(entry.title)}</h1><p>${escapeHtml(entry.content)}</p><p>Last modified by: ${escapeHtml(entry.lastModifiedBy)} at ${entry.lastModifiedAt}</p>`;
  } else {
    ctx.status = 404;
    ctx.body = 'Entry not found';
  }
});

// Update an existing entry
router.put('/entries/:entryId', async (ctx) => {
  const { entryId } = ctx.params;
  const { error, value } = updateSchema.validate(ctx.request.body);
  if (error) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }
  const { content, modifiedBy, summary } = value;
  const now = new Date().toISOString();

  const entry = await db.get('SELECT * FROM entries WHERE id = ?', entryId);

  if (entry) {
    await db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', 
      content, modifiedBy, now, entryId);

    const editId = uuidv4();
    await db.run('INSERT INTO edits (id, entryId, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?, ?)', 
      editId, entryId, modifiedBy, summary, now);

    ctx.body = { id: entryId, title: entry.title, content, lastModifiedBy: modifiedBy, lastModifiedAt: now };
  } else {
    ctx.status = 404;
    ctx.body = 'Entry not found';
  }
});

// View the history of edits for a specific entry
router.get('/entries/:entryId/edits', async (ctx) => {
  const { entryId } = ctx.params;
  const edits = await db.all('SELECT * FROM edits WHERE entryId = ?', entryId);

  if (edits.length > 0) {
    ctx.type = 'text/html';
    ctx.body = edits.map(edit => `<p>Modified by: ${escapeHtml(edit.modifiedBy)} at ${edit.modifiedAt} - ${escapeHtml(edit.summary)}</p>`).join('<br>');
  } else {
    ctx.status = 404;
    ctx.body = 'Entry not found';
  }
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

initDb().then(() => {
  app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
  });
});