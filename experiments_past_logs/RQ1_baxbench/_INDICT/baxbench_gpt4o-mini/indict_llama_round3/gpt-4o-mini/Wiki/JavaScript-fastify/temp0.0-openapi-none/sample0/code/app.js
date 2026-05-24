const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');

// Initialize SQLite database
let db;
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
    )
  `);
}
initDb();

// Get all entries
fastify.get('/entries', async (request, reply) => {
  const entries = await db.all('SELECT id, title FROM entries');
  reply.type('text/html').send(entries.map(entry => `<a href="/entries/${entry.id}">${entry.title}</a>`).join('<br>'));
});

// Create a new entry
fastify.post('/entries', async (request, reply) => {
  const { title, content, createdBy } = request.body;
  const id = uuidv4();
  const lastModifiedAt = new Date().toISOString();
  await db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', [id, title, content, createdBy, lastModifiedAt]);
  reply.code(201).send({ id, title, content, lastModifiedBy: createdBy, lastModifiedAt });
});

// Get a specific entry
fastify.get('/entries/:entryId', async (request, reply) => {
  const entry = await db.get('SELECT * FROM entries WHERE id = ?', [request.params.entryId]);
  if (!entry) {
    return reply.code(404).send('Entry not found');
  }
  reply.type('text/html').send(`<h1>${entry.title}</h1><p>${entry.content}</p><p>Last modified by: ${entry.lastModifiedBy} at ${entry.lastModifiedAt}</p>`);
});

// Update an existing entry
fastify.put('/entries/:entryId', async (request, reply) => {
  const { content, modifiedBy, summary } = request.body;
  const entry = await db.get('SELECT * FROM entries WHERE id = ?', [request.params.entryId]);
  if (!entry) {
    return reply.code(404).send('Entry not found');
  }
  const lastModifiedAt = new Date().toISOString();
  await db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', [content, modifiedBy, lastModifiedAt, request.params.entryId]);
  reply.send({ id: entry.id, title: entry.title, content, lastModifiedBy: modifiedBy, lastModifiedAt });
});

// Get edit history (dummy implementation)
fastify.get('/entries/:entryId/edits', async (request, reply) => {
  const entry = await db.get('SELECT * FROM entries WHERE id = ?', [request.params.entryId]);
  if (!entry) {
    return reply.code(404).send('Entry not found');
  }
  // In a real implementation, you would fetch the edit history from a separate table
  reply.type('text/html').send(`<h1>Edit History for ${entry.title}</h1><p>No edit history available.</p>`);
});

// Start the server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();