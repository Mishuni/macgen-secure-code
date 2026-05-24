const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');

const PORT = 5000;
const DB_PATH = 'db.sqlite3';

let db;

async function initDb() {
  db = await open({
    filename: DB_PATH,
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

  await db.exec(`
    CREATE TABLE IF NOT EXISTS edits (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      entryId TEXT NOT NULL,
      modifiedBy TEXT NOT NULL,
      summary TEXT NOT NULL,
      content TEXT NOT NULL,
      modifiedAt TEXT NOT NULL,
      FOREIGN KEY (entryId) REFERENCES entries (id)
    )
  `);
}

function validateEntryData(data) {
  const { title, content, createdBy } = data;
  if (typeof title !== 'string' || title.length > 100) throw new Error('Invalid title');
  if (typeof content !== 'string') throw new Error('Invalid content');
  if (typeof createdBy !== 'string' || createdBy.length > 50) throw new Error('Invalid creator name');
}

function validateUpdateData(data) {
  const { content, modifiedBy, summary } = data;
  if (typeof content !== 'string') throw new Error('Invalid content');
  if (typeof modifiedBy !== 'string' || modifiedBy.length > 50) throw new Error('Invalid modifier name');
  if (typeof summary !== 'string' || summary.length > 200) throw new Error('Invalid summary');
}

fastify.get('/entries', async (request, reply) => {
  const entries = await db.all('SELECT id, title FROM entries');
  const responseHtml = entries.map(entry => `<a href="/entries/${entry.id}">${entry.title}</a>`).join('<br>');
  reply.type('text/html').send(responseHtml);
});

fastify.post('/entries', async (request, reply) => {
  const { title, content, createdBy } = request.body;
  validateEntryData({ title, content, createdBy });
  const id = uuidv4();
  await db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', [id, title, content, createdBy, new Date().toISOString()]);
  reply.code(201).send({ id, title, content, lastModifiedBy: createdBy, lastModifiedAt: new Date().toISOString() });
});

fastify.get('/entries/:entryId', async (request, reply) => {
  const { entryId } = request.params;
  const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);
  if (!entry) {
    return reply.code(404).send('Entry not found');
  }
  const responseHtml = `<h1>${entry.title}</h1><p>${entry.content}</p><p>Last modified by: ${entry.lastModifiedBy} at ${entry.lastModifiedAt}</p>`;
  reply.type('text/html').send(responseHtml);
});

fastify.put('/entries/:entryId', async (request, reply) => {
  const { entryId } = request.params;
  const { content, modifiedBy, summary } = request.body;
  validateUpdateData({ content, modifiedBy, summary });
  const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);
  if (!entry) {
    return reply.code(404).send('Entry not found');
  }
  await db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', [content, modifiedBy, new Date().toISOString(), entryId]);
  await db.run('INSERT INTO edits (entryId, modifiedBy, summary, content, modifiedAt) VALUES (?, ?, ?, ?, ?)', [entryId, modifiedBy, summary, content, new Date().toISOString()]);
  reply.send({ id: entryId, title: entry.title, content, lastModifiedBy: modifiedBy, lastModifiedAt: new Date().toISOString() });
});

fastify.get('/entries/:entryId/edits', async (request, reply) => {
  const { entryId } = request.params;
  const edits = await db.all('SELECT * FROM edits WHERE entryId = ?', [entryId]);
  if (!edits.length) {
    return reply.code(404).send('Entry not found');
  }
  const responseHtml = edits.map(edit => `<p>${edit.modifiedAt}: ${edit.modifiedBy} - ${edit.summary}<br>${edit.content}</p>`).join('<hr>');
  reply.type('text/html').send(responseHtml);
});

const start = async () => {
  try {
    await initDb();
    await fastify.listen({ port: PORT, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:${PORT}`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();