const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const DB_PATH = 'db.sqlite3';

async function initDb() {
  const db = await open({
    filename: DB_PATH,
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      content TEXT NOT NULL,
      username TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  return db;
}

const dbPromise = initDb();

fastify.get('/messages', async (request, reply) => {
  const { limit = 10, offset = 0, sort = 'DESC' } = request.query;
  const db = await dbPromise;

  const maxLimit = 100;
  const safeLimit = Math.min(limit, maxLimit);
  const order = sort === 'ASC' ? 'ASC' : 'DESC';
  
  const messages = await db.all(`SELECT * FROM messages ORDER BY created_at ${order} LIMIT ? OFFSET ?`, [safeLimit, offset]);

  reply.type('text/html').send(JSON.stringify(messages));
});

fastify.post('/messages', async (request, reply) => {
  const { content, username } = request.body;

  if (typeof content !== 'string' || content.length > 500) {
    return reply.status(400).send({ error: 'Invalid content' });
  }
  if (typeof username !== 'string' || username.length > 50) {
    return reply.status(400).send({ error: 'Invalid username' });
  }

  const db = await dbPromise;
  await db.run('INSERT INTO messages (content, username) VALUES (?, ?)', [content, username]);

  reply.status(200).send({ message: 'Successful operation' });
});

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