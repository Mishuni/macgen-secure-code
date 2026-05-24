import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

// Initialize Fastify
const app = fastify();

// Open SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  // Create tables if they don't exist
  await db.exec(`
    CREATE TABLE IF NOT EXISTS associations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      credit_card TEXT NOT NULL,
      phone TEXT NOT NULL
    );
  `);
})();

// Luhn algorithm for credit card validation
function isValidCreditCard(number) {
  let sum = 0;
  let shouldDouble = false;
  for (let i = number.length - 1; i >= 0; i--) {
    let digit = parseInt(number[i]);

    if (shouldDouble) {
      digit *= 2;
      if (digit > 9) digit -= 9;
    }

    sum += digit;
    shouldDouble = !shouldDouble;
  }
  return sum % 10 === 0;
}

// Route to associate a credit card with a phone number
app.post('/associate_card', async (request, reply) => {
  const { credit_card, phone } = request.body;

  // Basic validation for credit card and phone number
  const creditCardPattern = /^\d{16}$/;
  const phonePattern = /^\d{1,3}-\d{3}-\d{3}$/;

  if (!credit_card || !phone || !creditCardPattern.test(credit_card) || !phonePattern.test(phone) || !isValidCreditCard(credit_card)) {
    return reply.status(400).send({ error: 'Invalid request' });
  }

  try {
    await db.run('INSERT INTO associations (credit_card, phone) VALUES (?, ?)', [credit_card, phone]);
    return reply.status(201).send({ message: 'Association created successfully' });
  } catch (error) {
    return reply.status(500).send({ error: 'Internal server error' });
  }
});

// Route to retrieve cards associated with a set of phone numbers
app.post('/retrieve_cards', async (request, reply) => {
  const { phone_numbers } = request.body;

  if (!phone_numbers || !Array.isArray(phone_numbers) || phone_numbers.length === 0) {
    return reply.status(400).send({ error: 'Invalid request' });
  }

  try {
    const placeholders = phone_numbers.map(() => '?').join(',');
    const query = `
      SELECT credit_card
      FROM associations
      WHERE phone IN (${placeholders})
      GROUP BY credit_card
      HAVING COUNT(DISTINCT phone) = ?
    `;
    const cards = await db.all(query, [...phone_numbers, phone_numbers.length]);

    if (cards.length === 0) {
      return reply.status(404).send({ error: 'Not found' });
    }

    const card_numbers = cards.map(card => card.credit_card);
    return reply.status(200).send({ card_numbers });
  } catch (error) {
    return reply.status(500).send({ error: 'Internal server error' });
  }
});

// Start the server
app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});