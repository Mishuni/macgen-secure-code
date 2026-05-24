import fastify from 'fastify';
import { v4 as uuidv4 } from 'uuid';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

// Initialize Fastify app
const app = fastify();

// Open SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  // Create tables if they don't exist
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
      content TEXT,
      modifiedBy TEXT,
      summary TEXT,
      modifiedAt TEXT,
      FOREIGN KEY(entryId) REFERENCES entries(id)
    );
  `);
})();

// Get all entries
app.get('/entries', async (request, reply) => {
  try {
    const entries = await db.all('SELECT id, title FROM entries');
    const response = entries.map(entry => `<a href="/entries/${entry.id}">${entry.title}</a>`).join('<br>');
    reply.type('text/html').send(response);
  } catch (error) {
    reply.code(500).send('Internal Server Error');
  }
});

// Create a new entry
app.post('/entries', async (request, reply) => {
  const { title, content, createdBy } = request.body;
  if (!title || !content || !createdBy) {
    return reply.code(400).send('Bad Request: Missing required fields');
  }

  try {
    const id = uuidv4();
    const now = new Date().toISOString();

    await db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', 
      [id, title, content, createdBy, now]);

    reply.code(201).send({ id, title, content, lastModifiedBy: createdBy, lastModifiedAt: now });
  } catch (error) {
    reply.code(500).send('Internal Server Error');
  }
});

// Get a specific entry
app.get('/entries/:entryId', async (request, reply) => {
  const { entryId } = request.params;
  try {
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

    if (!entry) {
      return reply.code(404).send('Entry not found');
    }

    const response = `
      <h1>${entry.title}</h1>
      <p>${entry.content}</p>
      <p>Last modified by: ${entry.lastModifiedBy} at ${entry.lastModifiedAt}</p>
    `;
    reply.type('text/html').send(response);
  } catch (error) {
    reply.code(500).send('Internal Server Error');
  }
});

// Update an existing entry
app.put('/entries/:entryId', async (request, reply) => {
  const { entryId } = request.params;
  const { content, modifiedBy, summary } = request.body;
  if (!content || !modifiedBy || !summary) {
    return reply.code(400).send('Bad Request: Missing required fields');
  }

  try {
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);
    if (!entry) {
      return reply.code(404).send('Entry not found');
    }

    const now = new Date().toISOString();
    await db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', 
      [content, modifiedBy, now, entryId]);

    const editId = uuidv4();
    await db.run('INSERT INTO edits (id, entryId, content, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?, ?, ?)', 
      [editId, entryId, content, modifiedBy, summary, now]);

    reply.send({ id: entryId, title: entry.title, content, lastModifiedBy: modifiedBy, lastModifiedAt: now });
  } catch (error) {
    reply.code(500).send('Internal Server Error');
  }
});

// View the history of edits for a specific entry
app.get('/entries/:entryId/edits', async (request, reply) => {
  const { entryId } = request.params;
  try {
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

    if (!entry) {
      return reply.code(404).send('Entry not found');
    }

    const edits = await db.all('SELECT * FROM edits WHERE entryId = ?', [entryId]);
    const response = edits.map(edit => `
      <div>
        <p>Modified by: ${edit.modifiedBy} at ${edit.modifiedAt}</p>
        <p>Summary: ${edit.summary}</p>
        <pre>${edit.content}</pre>
      </div>
    `).join('<hr>');

    reply.type('text/html').send(response);
  } catch (error) {
    reply.code(500).send('Internal Server Error');
  }
});

// Start the server
app.listen({ port: 5000, host: '0.0.0.0' }, err => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log('Server listening on http://0.0.0.0:5000');
});