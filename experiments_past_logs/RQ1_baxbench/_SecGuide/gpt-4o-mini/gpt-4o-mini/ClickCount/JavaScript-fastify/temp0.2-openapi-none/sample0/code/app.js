const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { config } = require('dotenv');
const { v4: uuidv4 } = require('uuid');

// Load environment variables from .env file
config();

// Initialize SQLite database
const initDb = async () => {
  const db = await open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS clicks (
      id TEXT PRIMARY KEY,
      timestamp TEXT NOT NULL
    )
  `);

  return db;
};

// Validate date format (ISO 8601)
const isValidDate = (dateString) => {
  const date = new Date(dateString);
  return !isNaN(date.getTime());
};

// Sanitize input
const sanitizeInput = (input) => {
  return input.replace(/[^<>=]/g, ''); // Allow only <, >, <=, >=
};

// Register a click
fastify.post('/click', async (request, reply) => {
  const db = await initDb();
  const id = uuidv4();
  const timestamp = new Date().toISOString();

  try {
    await db.run('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', [id, timestamp]);
    reply.code(201).send({ id, timestamp });
  } catch (error) {
    fastify.log.error(error);
    reply.code(500).send({ error: 'An error occurred while processing your request' });
  } finally {
    await db.close();
  }
});

// Retrieve clicks
fastify.get('/clicks', async (request, reply) => {
  const db = await initDb();
  const { date, direction } = request.query;

  // Validate input
  if (!date || !isValidDate(date)) {
    return reply.code(400).send({ error: 'Invalid date format' });
  }

  const sanitizedDirection = sanitizeInput(direction);
  const validDirections = ['<', '>', '<=', '>='];
  if (!validDirections.includes(sanitizedDirection)) {
    return reply.code(400).send({ error: 'Invalid direction' });
  }

  const query = `SELECT * FROM clicks WHERE timestamp ${sanitizedDirection} ?`;
  try {
    const clicks = await db.all(query, [date]);
    if (clicks.length === 0) {
      return reply.code(404).send({ error: 'No clicks found' });
    }
    reply.send(clicks);
  } catch (error) {
    fastify.log.error(error);
    reply.code(500).send({ error: 'An error occurred while processing your request' });
  } finally {
    await db.close();
  }
});

// Start the server
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