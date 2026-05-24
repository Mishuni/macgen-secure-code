const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const helmet = require('helmet');
const { body, param, validationResult } = require('express-validator');
const csurf = require('csurf');
const xss = require('xss');
const morgan = require('morgan');

const app = express();
app.use(express.json());
app.use(helmet());
app.use(csurf({ cookie: true }));
app.use(morgan('combined'));

let db;

// Initialize the database
(async () => {
  db = await open({
    filename: 'db.sqlite3',
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
})();

// Middleware for error logging
function logErrors(err, req, res, next) {
  console.error(err.message);
  next(err);
}

app.use(logErrors);

// Get all entries
app.get('/entries', async (req, res) => {
  try {
    const entries = await db.all('SELECT id, title FROM entries');
    const response = entries.map(entry => `<li><a href="/entries/${entry.id}">${xss(entry.title)}</a></li>`).join('');
    res.status(200).send(`<ul>${response}</ul>`);
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// Create a new entry
app.post('/entries', [
  body('title').isString().notEmpty(),
  body('content').isString().notEmpty(),
  body('createdBy').isString().notEmpty()
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  const { title, content, createdBy } = req.body;

  try {
    const id = uuidv4();
    const now = new Date().toISOString();
    await db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', [id, xss(title), xss(content), xss(createdBy), now]);
    res.status(201).json({ id, title: xss(title), content: xss(content), lastModifiedBy: xss(createdBy), lastModifiedAt: now });
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// Get a specific entry
app.get('/entries/:entryId', [
  param('entryId').isUUID()
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  const { entryId } = req.params;
  try {
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);
    if (!entry) {
      return res.status(404).send('Entry not found');
    }
    res.status(200).send(`<h1>${xss(entry.title)}</h1><p>${xss(entry.content)}</p><p>Last modified by: ${xss(entry.lastModifiedBy)} at ${entry.lastModifiedAt}</p>`);
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// Update an existing entry
app.put('/entries/:entryId', [
  param('entryId').isUUID(),
  body('content').isString().notEmpty(),
  body('modifiedBy').isString().notEmpty(),
  body('summary').isString().notEmpty()
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  const { entryId } = req.params;
  const { content, modifiedBy, summary } = req.body;

  try {
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);
    if (!entry) {
      return res.status(404).send('Entry not found');
    }

    const now = new Date().toISOString();
    await db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', [xss(content), xss(modifiedBy), now, entryId]);
    await db.run('INSERT INTO edits (id, entryId, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?, ?)', [uuidv4(), entryId, xss(modifiedBy), xss(summary), now]);
    res.status(200).json({ id: entryId, title: xss(entry.title), content: xss(content), lastModifiedBy: xss(modifiedBy), lastModifiedAt: now });
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// View the history of edits for a specific entry
app.get('/entries/:entryId/edits', [
  param('entryId').isUUID()
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  const { entryId } = req.params;
  try {
    const edits = await db.all('SELECT * FROM edits WHERE entryId = ?', [entryId]);
    if (edits.length === 0) {
      return res.status(404).send('Entry not found');
    }
    const response = edits.map(edit => `<li>${xss(edit.modifiedBy)} modified on ${edit.modifiedAt}: ${xss(edit.summary)}</li>`).join('');
    res.status(200).send(`<ul>${response}</ul>`);
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server is running on http://0.0.0.0:5000');
});