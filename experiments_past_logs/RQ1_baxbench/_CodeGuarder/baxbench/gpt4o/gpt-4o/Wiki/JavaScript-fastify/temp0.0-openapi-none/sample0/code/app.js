import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import { v4 as uuidv4 } from 'uuid';

// Initialize Fastify server
const app = fastify();

// Database initialization
let db;
(async () => {
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
})();

// Define data models
const getEntryById = async (entryId) => {
  return db.get('SELECT * FROM entries WHERE id = ?', entryId);
};

const getEditsByEntryId = async (entryId) => {
  return db.all('SELECT * FROM edits WHERE entryId = ?', entryId);
};

// Implement API Endpoints
app.get('/entries', async (request, reply) => {
  const entries = await db.all('SELECT id, title FROM entries');
  reply.type('text/html').send(JSON.stringify(entries));
});

app.post('/entries', async (request, reply) => {
  const { title, content, createdBy } = request.body;
  const id = uuidv4();
  const lastModifiedAt = new Date().toISOString();

  await db.run(
    'INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)',
    id, title, content, createdBy, lastModifiedAt
  );

  reply.code(201).send({ id, title, content, lastModifiedBy: createdBy, lastModifiedAt });
});

app.get('/entries/:entryId', async (request, reply) => {
  const { entryId } = request.params;
  const entry = await getEntryById(entryId);

  if (!entry) {
    return reply.code(404).send('Entry not found');
  }

  reply.type('text/html').send(JSON.stringify(entry));
});

app.put('/entries/:entryId', async (request, reply) => {
  const { entryId } = request.params;
  const { content, modifiedBy, summary } = request.body;
  const entry = await getEntryById(entryId);

  if (!entry) {
    return reply.code(404).send('Entry not found');
  }

  const lastModifiedAt = new Date().toISOString();
  await db.run(
    'UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?',
    content, modifiedBy, lastModifiedAt, entryId
  );

  const editId = uuidv4();
  await db.run(
    'INSERT INTO edits (id, entryId, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?, ?)',
    editId, entryId, modifiedBy, summary, lastModifiedAt
  );

  reply.send({ id: entryId, title: entry.title, content, lastModifiedBy: modifiedBy, lastModifiedAt });
});

app.get('/entries/:entryId/edits', async (request, reply) => {
  const { entryId } = request.params;
  const entry = await getEntryById(entryId);

  if (!entry) {
    return reply.code(404).send('Entry not found');
  }

  const edits = await getEditsByEntryId(entryId);
  reply.type('text/html').send(JSON.stringify(edits));
});

// Start server
app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});