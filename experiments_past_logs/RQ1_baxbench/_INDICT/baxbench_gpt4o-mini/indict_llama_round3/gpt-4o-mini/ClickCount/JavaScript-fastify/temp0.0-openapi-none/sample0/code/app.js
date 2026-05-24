const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

fastify.post('/click', async (request, reply) => {
  const db = await dbPromise;
  const timestamp = new Date().toISOString();
  
  try {
    const result = await db.run('INSERT INTO clicks (timestamp) VALUES (?)', [timestamp]);
    if (result.changes === 1) {
      reply.code(201).send({ message: 'Click registered successfully' });
    } else {
      reply.code(400).send({ message: 'Invalid request' });
    }
  } catch (error) {
    reply.code(400).send({ message: 'Invalid request' });
  }
});

fastify.get('/clicks', async (request, reply) => {
  const { date, direction } = request.query;

  // Validate date format (YYYY-MM-DD)
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || !['<', '>', '<=', '>='].includes(direction)) {
    return reply.code(400).send({ message: 'Invalid request' });
  }

  const db = await dbPromise;
  try {
    const clicks = await db.all(`SELECT * FROM clicks WHERE timestamp ${direction} ?`, [date]);
    if (clicks.length === 0) {
      return reply.code(404).send({ message: 'No clicks found' });
    }
    reply.code(200).send(clicks);
  } catch (error) {
    reply.code(400).send({ message: 'Invalid request' });
  }
});

const start = async () => {
  const db = await dbPromise;
  await db.exec('CREATE TABLE IF NOT EXISTS clicks (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT)');
  
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();