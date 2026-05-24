
const fastify = require('fastify')();
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');

dotenv.config();

const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

async function setupDatabase() {
  const db = await dbPromise;
  await db.exec(`
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      content TEXT NOT NULL,
      username TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `);
}

fastify.get('/messages', async (request, reply) => {
  const { limit = 10, offset = 0, sort = 'DESC' } = request.query;
  const db = await dbPromise;
  const messages = await db.all(
    `SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`,
    [parseInt(limit), parseInt(offset)]
  );
  reply.type('text/html').send(JSON.stringify(messages));
});

fastify.post('/messages', async (request, reply) => {
  const { content, username } = request.body;
  if (!content || !username) {
    return reply.status(400).send('Invalid input');
  }
  const db = await dbPromise;
  await db.run(
    'INSERT INTO messages (content, username) VALUES (?, ?)',
    [content, username]
  );
  reply.send('Successful operation');
});

const start = async () => {
  try {
    await setupDatabase();
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server listening on http://0.0.0.0:5000');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();