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
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  // Create clicks table if it doesn't exist
  await db.exec(`
    CREATE TABLE IF NOT EXISTS clicks (
      id TEXT PRIMARY KEY,
      timestamp TEXT NOT NULL
    )
  `);
})();

// Register a click
app.post('/click', async (request, reply) => {
  try {
    const id = uuidv4();
    const timestamp = new Date().toISOString();

    await db.run('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', [id, timestamp]);

    reply.code(201).send({ message: 'Click registered successfully' });
  } catch (error) {
    reply.code(400).send({ error: 'Invalid request' });
  }
});

// Retrieve clicks
app.get('/clicks', async (request, reply) => {
  const { date, direction } = request.query;

  if (!date || !direction || !['<', '>', '<=', '>='].includes(direction)) {
    return reply.code(400).send({ error: 'Invalid request' });
  }

  try {
    const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
    const clicks = await db.all(query, [date]);

    if (clicks.length === 0) {
      return reply.code(404).send({ error: 'No clicks found' });
    }

    reply.code(200).send(clicks);
  } catch (error) {
    reply.code(400).send({ error: 'Invalid request' });
  }
});

// Start the server
app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});