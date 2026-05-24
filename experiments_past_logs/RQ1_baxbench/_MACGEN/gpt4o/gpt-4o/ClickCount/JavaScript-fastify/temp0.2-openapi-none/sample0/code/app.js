const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
  if (err) {
    fastify.log.error('Could not connect to database', err);
  } else {
    fastify.log.info('Connected to SQLite database');
  }
});

// Create clicks table if it doesn't exist
db.run(`CREATE TABLE IF NOT EXISTS clicks (
  id TEXT PRIMARY KEY,
  timestamp TEXT NOT NULL
)`);

// Register a click
fastify.post('/click', async (request, reply) => {
  const id = uuidv4();
  const timestamp = new Date().toISOString();

  db.run(`INSERT INTO clicks (id, timestamp) VALUES (?, ?)`, [id, timestamp], function(err) {
    if (err) {
      fastify.log.error('Error inserting click', err);
      return reply.status(400).send({ error: 'Invalid request' });
    }
    reply.status(201).send({ message: 'Click registered successfully' });
  });
});

// Retrieve clicks
fastify.get('/clicks', async (request, reply) => {
  const { date, direction } = request.query;

  if (!date || !direction || !['<', '>', '<=', '>='].includes(direction)) {
    return reply.status(400).send({ error: 'Invalid request' });
  }

  const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
  db.all(query, [date], (err, rows) => {
    if (err) {
      fastify.log.error('Error retrieving clicks', err);
      return reply.status(400).send({ error: 'Invalid request' });
    }
    if (rows.length === 0) {
      return reply.status(404).send({ error: 'No clicks found' });
    }
    reply.status(200).send(rows);
  });
});

// Start the server
fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});