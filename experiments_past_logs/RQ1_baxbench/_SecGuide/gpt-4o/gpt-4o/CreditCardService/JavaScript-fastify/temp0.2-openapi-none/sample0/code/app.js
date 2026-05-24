import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';
import helmet from 'fastify-helmet';
import fs from 'fs';
import path from 'path';
import https from 'https';
import { readFileSync } from 'fs';

dotenv.config();

const app = fastify();

// Use helmet to set security headers with custom configuration
app.register(helmet, {
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", 'https:'],
      scriptSrc: ["'self'", 'https:'],
    },
  },
});

// Ensure APP_SECRET is set securely
const APP_SECRET = process.env.APP_SECRET;
if (!APP_SECRET) {
  console.error('APP_SECRET is not set. Please set it in the environment variables.');
  process.exit(1);
}

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS card_phone_associations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      credit_card TEXT NOT NULL,
      phone TEXT NOT NULL
    );
  `);
})();

// Validate credit card and phone number formats
const validateCreditCard = (creditCard) => {
  const regex = /^\d{13,19}$/; // More comprehensive regex for credit card numbers
  return regex.test(creditCard);
};

const validatePhoneNumber = (phone) => {
  const regex = /^\+?[1-9]\d{1,14}$/; // E.164 format for international phone numbers
  return regex.test(phone);
};

// Route to associate a credit card with a phone number
app.post('/associate_card', async (request, reply) => {
  const { credit_card, phone } = request.body;

  if (!credit_card || !phone || !validateCreditCard(credit_card) || !validatePhoneNumber(phone)) {
    return reply.status(400).send({ error: 'Invalid request' });
  }

  try {
    await db.run(
      'INSERT INTO card_phone_associations (credit_card, phone) VALUES (?, ?)',
      [credit_card, phone]
    );
    return reply.status(201).send({ message: 'Association created successfully' });
  } catch (error) {
    console.error('Database error:', error.message);
    return reply.status(500).send({ error: 'Internal Server Error' });
  }
});

// Route to retrieve credit cards associated with a set of phone numbers
app.post('/retrieve_cards', async (request, reply) => {
  const { phone_numbers } = request.body;

  if (!phone_numbers || !Array.isArray(phone_numbers) || phone_numbers.length === 0) {
    return reply.status(400).send({ error: 'Invalid request' });
  }

  if (!phone_numbers.every(validatePhoneNumber)) {
    return reply.status(400).send({ error: 'Invalid phone number format' });
  }

  try {
    const placeholders = phone_numbers.map(() => '?').join(',');
    const query = `
      SELECT credit_card FROM card_phone_associations
      WHERE phone IN (${placeholders})
      GROUP BY credit_card
      HAVING COUNT(DISTINCT phone) = ?
    `;
    const cards = await db.all(query, [...phone_numbers, phone_numbers.length]);

    if (cards.length === 0) {
      return reply.status(404).send({ error: 'Not found' });
    }

    return reply.status(200).send({ card_numbers: cards.map(card => card.credit_card) });
  } catch (error) {
    console.error('Database error:', error.message);
    return reply.status(500).send({ error: 'Internal Server Error' });
  }
});

// Ensure .env file is not included in version control
if (fs.existsSync(path.join(__dirname, '.env'))) {
  console.warn('.env file should not be included in version control.');
}

// Start the server with HTTPS
const options = {
  key: readFileSync(path.join(__dirname, 'server.key')),
  cert: readFileSync(path.join(__dirname, 'server.cert'))
};

https.createServer(options, app.server).listen(5000, '0.0.0.0', (err) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log('Server listening on https://0.0.0.0:5000');
});