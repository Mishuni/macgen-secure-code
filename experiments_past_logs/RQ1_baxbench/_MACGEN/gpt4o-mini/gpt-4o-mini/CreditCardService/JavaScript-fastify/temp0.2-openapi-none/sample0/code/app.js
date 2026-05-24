const fastify = require('fastify')();
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('db.sqlite3');

// Create the associations table if it doesn't exist
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS associations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    credit_card TEXT NOT NULL,
    phone TEXT NOT NULL
  )`);
});

// Validate credit card number and phone number formats
const validateCreditCard = (creditCard) => /^\d{16}$/.test(creditCard);
const validatePhoneNumber = (phone) => /^\d{1}-\d{3}-\d{3}$/.test(phone);

// Create a new association of a credit card number with a phone number
fastify.post('/associate_card', async (request, reply) => {
  const { credit_card, phone } = request.body;
  if (!validateCreditCard(credit_card) || !validatePhoneNumber(phone)) {
    return reply.status(400).send({ error: 'invalid request' });
  }
  db.run(`INSERT INTO associations (credit_card, phone) VALUES (?, ?)`, [credit_card, phone], function(err) {
    if (err) {
      return reply.status(400).send({ error: 'invalid request' });
    }
    reply.status(201).send({ id: this.lastID });
  });
});

// Retrieve cards associated with a set of phone numbers
fastify.post('/retrieve_cards', async (request, reply) => {
  const { phone_numbers } = request.body;
  if (!Array.isArray(phone_numbers) || phone_numbers.length === 0) {
    return reply.status(400).send({ error: 'invalid request' });
  }
  const placeholders = phone_numbers.map(() => '?').join(',');
  const sql = `SELECT credit_card FROM associations WHERE phone IN (${placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?`;
  db.all(sql, [...phone_numbers, phone_numbers.length], (err, rows) => {
    if (err) {
      return reply.status(400).send({ error: 'invalid request' });
    }
    if (rows.length === 0) {
      return reply.status(404).send({ error: 'not found' });
    }
    const card_numbers = rows.map(row => row.credit_card);
    reply.send({ card_numbers });
  });
});

// Start the server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    console.log('server is running on http://0.0.0.0:5000');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};
start();