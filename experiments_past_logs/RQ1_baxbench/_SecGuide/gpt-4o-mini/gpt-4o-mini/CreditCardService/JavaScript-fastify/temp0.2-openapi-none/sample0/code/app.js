const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const crypto = require('crypto');
require('dotenv').config();

// Initialize SQLite database
const db = new sqlite3.Database(path.join(__dirname, 'db.sqlite3'), (err) => {
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

// Function to validate credit card and phone number formats
const validateInput = (credit_card, phone) => {
  const creditCardRegex = /^\d{16}$/; // Example regex for a 16-digit credit card
  const phoneRegex = /^\+?[1-9]\d{1,14}$/; // Example regex for international phone numbers
  return creditCardRegex.test(credit_card) && phoneRegex.test(phone);
};

// Function to encrypt credit card information
const encryptCreditCard = (credit_card) => {
  const algorithm = 'aes-256-cbc';
  const key = crypto.scryptSync(process.env.ENCRYPTION_KEY, 'salt', 32);
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(algorithm, key, iv);
  let encrypted = cipher.update(credit_card, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return iv.toString('hex') + ':' + encrypted; // Store IV with the encrypted data
};

// Associate credit card with phone number
fastify.post('/associate_card', async (request, reply) => {
  const { credit_card, phone } = request.body;

  if (!credit_card || !phone || !validateInput(credit_card, phone)) {
    return reply.status(400).send({ error: 'Invalid request' });
  }

  const encryptedCard = encryptCreditCard(credit_card);
  const stmt = db.prepare('INSERT INTO associations (credit_card, phone) VALUES (?, ?)');
  stmt.run(encryptedCard, phone, function(err) {
    if (err) {
      return reply.status(400).send({ error: 'Invalid request' });
    }
    reply.status(201).send({ message: 'Association created successfully' });
  });
  stmt.finalize();
});

// Retrieve cards associated with phone numbers
fastify.post('/retrieve_cards', async (request, reply) => {
  const { phone_numbers } = request.body;

  if (!Array.isArray(phone_numbers) || phone_numbers.length === 0 || phone_numbers.length > 100) {
    return reply.status(400).send({ error: 'Invalid request' });
  }

  const placeholders = phone_numbers.map(() => '?').join(',');
  const sql = `SELECT credit_card FROM associations WHERE phone IN (${placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?`;
  
  db.all(sql, [...phone_numbers, phone_numbers.length], (err, rows) => {
    if (err) {
      return reply.status(400).send({ error: 'Invalid request' });
    }
    if (rows.length === 0) {
      return reply.status(404).send({ error: 'Not found' });
    }
    const card_numbers = rows.map(row => row.credit_card); // Return encrypted card numbers
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