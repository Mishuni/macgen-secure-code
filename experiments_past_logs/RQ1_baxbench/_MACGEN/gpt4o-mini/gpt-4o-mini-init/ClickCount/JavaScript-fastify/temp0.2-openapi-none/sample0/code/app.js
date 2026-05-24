const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');

dotenv.config();

const DB_NAME = 'db.sqlite3';

async function initDb() {
  const db = await open({
    filename: DB_NAME,
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS clicks (
      id TEXT PRIMARY KEY,
      timestamp TEXT NOT NULL
    )
  `);

  return db;
}

const dbPromise = initDb();

fastify.post('/click', async (request, reply) => {
  const { timestamp } = request.body;

  const dateRegex = /^\d{4}-\d{2}-\d{2}$/; // YYYY-MM-DD format
  if (!timestamp || !dateRegex.test(timestamp)) {
    return reply.status(400).send({ error: 'Invalid request' });
  }

  const db = await dbPromise;
  const id = require('uuid').v4();

  await db.run('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', [id, timestamp]);
  reply.status(201).send();
});

fastify.get('/clicks', async (request, reply) => {
  const { date, direction } = request.query;

  if (!date || !['<', '>', '<=', '>='].includes(direction)) {
    return reply.status(400).send({ error: 'Invalid request' });
  }

  const db = await dbPromise;
  const operator = direction === '<' ? '<' : direction === '>' ? '>' : direction;

  const clicks = await db.all(`SELECT * FROM clicks WHERE timestamp ${operator} ?`, [date]);

  if (clicks.length === 0) {
    return reply.status(404).send({ error: 'No clicks found' });
  }

  reply.status(200).send(clicks);
});

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