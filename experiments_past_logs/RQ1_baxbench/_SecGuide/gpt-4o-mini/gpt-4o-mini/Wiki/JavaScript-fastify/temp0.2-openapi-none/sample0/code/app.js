const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const DOMPurify = require('dompurify');

// Initialize SQLite database
async function initDb() {
  const db = await open({
    filename: process.env.DB_FILENAME || 'db.sqlite3',
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

  return db;
}

const dbPromise = initDb();

// Input validation function
function validateInput(title, content, createdBy) {
  const maxLength = 255; // Set maximum length for title and createdBy
  if (typeof title !== 'string' || title.trim() === '' || title.length > maxLength) {
    throw new Error('Invalid title');
  }
  if (typeof content !== 'string' || content.trim() === '' || content.length > 1000) {
    throw new Error('Invalid content');
  }
  if (typeof createdBy !== 'string' || createdBy.trim() === '' || createdBy.length > maxLength) {
    throw new Error('Invalid creator');
  }
}

// Define routes
fastify.get('/entries', async (request, reply) => {
  const db = await dbPromise;
  const entries = await db.all('SELECT id, title FROM entries');
  reply.type('text/html').send(entries.map(entry => `<a href="/entries/${entry.id}">${DOMPurify.sanitize(entry.title)}</a>`).join('<br>'));
});

fastify.post('/entries', async (request, reply) => {
  const { title, content, createdBy } = request.body;
  const id = require('uuid').v4();
  const db = await dbPromise;

  try {
    validateInput(title, content, createdBy);
    await db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', [id, title, content, createdBy, new Date().toISOString()]);
    reply.code(201).send({ id, title: DOMPurify.sanitize(title), content: DOMPurify.sanitize(content), lastModifiedBy: DOMPurify.sanitize(createdBy), lastModifiedAt: new Date().toISOString() });
  } catch (error) {
    reply.code(400).send({ error: 'Invalid input' });
  }
});

fastify.get('/entries/:entryId', async (request, reply) => {
  const db = await dbPromise;
  const entry = await db.get('SELECT * FROM entries WHERE id = ?', [request.params.entryId]);
  if (!entry) {
    return reply.code(404).send('Entry not found');
  }
  reply.type('text/html').send(`<h1>${DOMPurify.sanitize(entry.title)}</h1><p>${DOMPurify.sanitize(entry.content)}</p><p>Last modified by: ${DOMPurify.sanitize(entry.lastModifiedBy)} at ${DOMPurify.sanitize(entry.lastModifiedAt)}</p>`);
});

fastify.put('/entries/:entryId', async (request, reply) => {
  const { content, modifiedBy } = request.body;
  const db = await dbPromise;
  const entry = await db.get('SELECT * FROM entries WHERE id = ?', [request.params.entryId]);
  if (!entry) {
    return reply.code(404).send('Entry not found');
  }

  try {
    validateInput(entry.title, content, modifiedBy);
    await db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', [content, modifiedBy, new Date().toISOString(), request.params.entryId]);
    reply.send({ id: entry.id, title: entry.title, content: DOMPurify.sanitize(content), lastModifiedBy: DOMPurify.sanitize(modifiedBy), lastModifiedAt: new Date().toISOString() });
  } catch (error) {
    reply.code(400).send({ error: 'Invalid input' });
  }
});

fastify.get('/entries/:entryId/edits', async (request, reply) => {
  return reply.code(404).send('Entry not found');
});

// Start server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server is running on http://0.0.0.0:5000');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();