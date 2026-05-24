const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// Initialize SQLite database
const db = new sqlite3.Database(path.join(__dirname, 'db.sqlite3'), (err) => {
  if (err) {
    fastify.log.error('Could not connect to database', err);
  } else {
    fastify.log.info('Connected to SQLite database');
  }
});

// Create table for storing credit card and phone associations
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS card_phone_associations (
    credit_card TEXT NOT NULL,
    phone TEXT NOT NULL,
    PRIMARY KEY (credit_card, phone)
  )`);
});

// Endpoint to associate a credit card with a phone number
fastify.post('/associate_card', async (request, reply) => {
  const { credit_card, phone } = request.body;

  if (!credit_card || !phone) {
    return reply.status(400).send({ error: 'Invalid request' });
  }

  const stmt = db.prepare('INSERT INTO card_phone_associations (credit_card, phone) VALUES (?, ?)');
  stmt.run(credit_card, phone, (err) => {
    if (err) {
      return reply.status(400).send({ error: 'Invalid request' });
    }
    reply.status(201).send({ message: 'Association created successfully' });
  });
  stmt.finalize();
});

// Endpoint to retrieve credit cards associated with a set of phone numbers
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
      return reply.status(400).send({ error: 'Invalid request' });
    }
    if (rows.length === 0) {
      return reply.status(404).send({ error: 'Not found' });
    }
    const card_numbers = rows.map(row => row.credit_card);
    reply.status(200).send({ card_numbers });
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