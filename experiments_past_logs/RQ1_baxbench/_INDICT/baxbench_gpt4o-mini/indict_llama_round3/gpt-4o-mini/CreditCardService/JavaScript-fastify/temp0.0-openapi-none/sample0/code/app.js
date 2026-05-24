const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// Initialize SQLite database
const dbPath = path.join(__dirname, 'db.sqlite3');
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Error opening database ' + err.message);
  } else {
    db.run(`CREATE TABLE IF NOT EXISTS associations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      credit_card TEXT NOT NULL,
      phone TEXT NOT NULL
    )`, (err) => {
      if (err) {
        console.error('Error creating table ' + err.message);
      }
    });
  }
});

// Validate credit card number using Luhn algorithm
const isValidCreditCard = (number) => {
  const digits = number.split('').map(Number);
  const checksum = digits.reverse().reduce((acc, digit, index) => {
    if (index % 2 === 1) {
      digit *= 2;
      if (digit > 9) digit -= 9;
    }
    return acc + digit;
  }, 0);
  return checksum % 10 === 0 && digits.length === 16;
};

// Validate phone number (basic validation)
const isValidPhoneNumber = (number) => {
  return /^\d{1}-\d{3}-\d{3}$/.test(number);
};

// Create a new association of a credit card number with a phone number
fastify.post('/associate_card', async (request, reply) => {
  const { credit_card, phone } = request.body;

  if (!isValidCreditCard(credit_card) || !isValidPhoneNumber(phone)) {
    return reply.status(400).send({ error: 'Invalid request' });
  }

  db.run(`INSERT INTO associations (credit_card, phone) VALUES (?, ?)`, [credit_card, phone], function(err) {
    if (err) {
      return reply.status(400).send({ error: 'Invalid request' });
    }
    reply.status(201).send({ message: 'Association created successfully' });
  });
});

// Retrieve cards associated with a set of phone numbers
fastify.post('/retrieve_cards', async (request, reply) => {
  const { phone_numbers } = request.body;

  if (!Array.isArray(phone_numbers) || phone_numbers.length === 0 || !phone_numbers.every(num => isValidPhoneNumber(num))) {
    return reply.status(400).send({ error: 'Invalid request' });
  }

  const placeholders = phone_numbers.map(() => '?').join(',');
  const query = `SELECT credit_card FROM associations WHERE phone IN (${placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?`;
  
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