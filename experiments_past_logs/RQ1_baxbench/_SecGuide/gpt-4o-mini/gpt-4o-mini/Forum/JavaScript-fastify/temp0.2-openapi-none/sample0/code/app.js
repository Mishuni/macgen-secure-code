const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

fastify.register(require('@fastify/cookie'));

// Whitelist for sort options
const validSortOptions = ['ASC', 'DESC'];

fastify.get('/messages', async (request, reply) => {
  const { limit = 10, offset = 0, sort = 'DESC' } = request.query;

  // Validate sort parameter
  if (!validSortOptions.includes(sort)) {
    return reply.status(400).send({ error: 'Invalid sort option' });
  }

  const db = await dbPromise;
  const messages = await db.all(`SELECT * FROM messages ORDER BY id ${sort} LIMIT ? OFFSET ?`, [limit, offset]);
  
  reply.type('text/html').send(messages.map(msg => `<div><strong>${escapeHtml(msg.username)}:</strong> ${escapeHtml(msg.content)}</div>`).join(''));
});

fastify.post('/messages', async (request, reply) => {
  const { content, username } = request.body;

  // Input validation
  if (!content || !username || content.length > 500 || username.length > 100) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  // Sanitize input
  const sanitizedContent = escapeHtml(content);
  const sanitizedUsername = escapeHtml(username);

  const db = await dbPromise;
  await db.run('INSERT INTO messages (content, username) VALUES (?, ?)', [sanitizedContent, sanitizedUsername]);
  
  reply.status(200).send({ message: 'Successful operation' });
});

fastify.addHook('onReady', async () => {
  const db = await dbPromise;
  await db.exec('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, username TEXT)');
});

function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

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