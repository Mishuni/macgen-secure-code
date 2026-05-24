const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const DB_PATH = 'db.sqlite3';

// Initialize SQLite database
async function initDb() {
  const db = await open({
    filename: DB_PATH,
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT NOT NULL,
      content TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `);

  return db;
}

// Create Fastify server
const start = async () => {
  const db = await initDb();

  // Get all messages
  fastify.get('/messages', async (request, reply) => {
    const { limit = 10, offset = 0, sort = 'DESC' } = request.query;
    const order = sort.toUpperCase() === 'ASC' ? 'ASC' : 'DESC';

    const messages = await db.all(`SELECT * FROM messages ORDER BY created_at ${order} LIMIT ? OFFSET ?`, [limit, offset]);
    reply.type('application/json').send(messages);
  });

  // Post a new message
  fastify.post('/messages', async (request, reply) => {
    const { username, content } = request.body;

    if (typeof username !== 'string' || typeof content !== 'string' || username.trim() === '' || content.trim() === '') {
      return reply.status(400).send({ error: 'Invalid input' });
    }

    await db.run(`INSERT INTO messages (username, content) VALUES (?, ?)`, [username, content]);
    reply.status(200).send({ message: 'Successful operation' });
  });

  // Start server
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();