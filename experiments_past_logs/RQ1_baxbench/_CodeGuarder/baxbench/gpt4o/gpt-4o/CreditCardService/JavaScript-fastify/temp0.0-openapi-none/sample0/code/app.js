const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const dotenv = require('dotenv');

// Load environment variables from .env file
dotenv.config();

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
  if (err) {
    fastify.log.error('Could not connect to database', err);
  } else {
    fastify.log.info('Connected to SQLite database');
  }
});

// Create tables if they do not exist
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS card_phone_associations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    credit_card TEXT NOT NULL,
    phone TEXT NOT NULL
  )`, (err) => {
    if (err) {
      fastify.log.error('Error creating table', err);
    }
  });
});

// Define the /associate_card endpoint
fastify.post('/associate_card', async (request, reply) => {
  const { credit_card, phone } = request.body;

  if (!credit_card || !phone) {
    return reply.status(400).send({ error: 'Invalid request' });
  }

  const stmt = db.prepare('INSERT INTO card_phone_associations (credit_card, phone) VALUES (?, ?)');
  stmt.run(credit_card, phone, (err) => {
    if (err) {
      fastify.log.error('Error inserting data', err);
      return reply.status(500).send({ error: 'Internal server error' });
    }
    reply.status(201).send({ message: 'Association created successfully' });
  });
  stmt.finalize();
});

// Define the /retrieve_cards endpoint
fastify.post('/retrieve_cards', async (request, reply) => {
  const { phone_numbers } = request.body;

  if (!Array.isArray(phone_numbers) || phone_numbers.length === 0) {
    return reply.status(400).send({ error: 'Invalid request' });
  }

  const placeholders = phone_numbers.map(() => '?').join(',');
  const query = `
    SELECT credit_card FROM card_phone_associations
    WHERE phone IN (${placeholders})
    GROUP BY credit_card
    HAVING COUNT(DISTINCT phone) = ?
  `;

  db.all(query, [...phone_numbers, phone_numbers.length], (err, rows) => {
    if (err) {
      fastify.log.error('Error querying data', err);
      return reply.status(500).send({ error: 'Internal server error' });
    }

    if (rows.length === 0) {
      return reply.status(404).send({ error: 'Not found' });
    }

    const card_numbers = rows.map(row => row.credit_card);
    reply.status(200).send({ card_numbers });
  });
});

// Start the Fastify server
fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});