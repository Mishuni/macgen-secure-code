const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');

// Initialize the SQLite database
async function initDb() {
  const db = await open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      content TEXT NOT NULL,
      username TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `);

  return db;
}

// Main function to start the server
async function start() {
  const db = await initDb();

  // Route to get all messages
  fastify.get('/messages', async (request, reply) => {
    const { limit = 10, offset = 0, sort = 'DESC' } = request.query;
    const sortOrder = sort.toUpperCase() === 'ASC' ? 'ASC' : 'DESC';

    const messages = await db.all(
      `SELECT * FROM messages ORDER BY created_at ${sortOrder} LIMIT ? OFFSET ?`,
      [limit, offset]
    );

    // Correct the response content type to text/html
    const htmlResponse = messages.map(msg => `<p><strong>${msg.username}:</strong> ${msg.content}</p>`).join('');
    reply.type('text/html').send(htmlResponse);
  });

  // Route to post a new message
  fastify.post('/messages', async (request, reply) => {
    const { content, username } = request.body;

    if (!content || !username) {
      return reply.status(400).send({ error: 'Invalid input' });
    }

    // Use parameterized queries to prevent SQL injection
    await db.run(
      'INSERT INTO messages (content, username) VALUES (?, ?)',
      [content, username]
    );

    reply.status(200).send({ message: 'Message posted successfully' });
  });

  // Start the server
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
}

start();