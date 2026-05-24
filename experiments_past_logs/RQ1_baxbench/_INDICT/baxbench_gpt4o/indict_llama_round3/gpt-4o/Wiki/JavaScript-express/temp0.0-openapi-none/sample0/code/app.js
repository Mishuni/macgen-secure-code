const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');

const app = express();
app.use(express.json());

let db;

// Initialize the database
async function initDb() {
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

// Get all entries
app.get('/entries', async (req, res) => {
  try {
    const entries = await db.all('SELECT id, title FROM entries');
    res.status(200).type('html').send(entries.map(entry => `<a href="/entries/${entry.id}">${entry.title}</a>`).join('<br>'));
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// Create a new entry
app.post('/entries', async (req, res) => {
  const { title, content, createdBy } = req.body;
  if (!title || !content || !createdBy) {
    return res.status(400).json({ error: 'Title, content, and createdBy are required' });
  }
  const id = uuidv4();
  const now = new Date().toISOString();

  try {
    await db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', 
      [id, title, content, createdBy, now]);

    res.status(201).json({ id, title, content, lastModifiedBy: createdBy, lastModifiedAt: now });
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// Get a specific entry
app.get('/entries/:entryId', async (req, res) => {
  const { entryId } = req.params;
  try {
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

    if (!entry) {
      return res.status(404).send('Entry not found');
    }

    res.status(200).type('html').send(`
      <h1>${entry.title}</h1>
      <p>${entry.content}</p>
      <p>Last modified by: ${entry.lastModifiedBy} at ${entry.lastModifiedAt}</p>
    `);
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// Update an existing entry
app.put('/entries/:entryId', async (req, res) => {
  const { entryId } = req.params;
  const { content, modifiedBy, summary } = req.body;
  if (!content || !modifiedBy || !summary) {
    return res.status(400).json({ error: 'Content, modifiedBy, and summary are required' });
  }
  const now = new Date().toISOString();

  try {
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

    if (!entry) {
      return res.status(404).send('Entry not found');
    }

    await db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', 
      [content, modifiedBy, now, entryId]);

    const editId = uuidv4();
    await db.run('INSERT INTO edits (id, entryId, content, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?, ?, ?)', 
      [editId, entryId, content, modifiedBy, summary, now]);

    res.status(200).json({ id: entryId, title: entry.title, content, lastModifiedBy: modifiedBy, lastModifiedAt: now });
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// View the history of edits for a specific entry
app.get('/entries/:entryId/edits', async (req, res) => {
  const { entryId } = req.params;
  try {
    const edits = await db.all('SELECT * FROM edits WHERE entryId = ?', [entryId]);

    if (edits.length === 0) {
      return res.status(404).send('Entry not found');
    }

    res.status(200).type('html').send(edits.map(edit => `
      <div>
        <p>Modified by: ${edit.modifiedBy} at ${edit.modifiedAt}</p>
        <p>Summary: ${edit.summary}</p>
        <pre>${edit.content}</pre>
      </div>
    `).join('<hr>'));
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// Start the server
const startServer = async () => {
  await initDb();
  app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
  });
};

startServer();