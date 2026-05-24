const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

const app = new Koa();
const router = new Router();

// Database setup
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database,
  });

  // Create tables if they don't exist
  await db.exec(`
    CREATE TABLE IF NOT EXISTS credit_card_associations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      credit_card TEXT NOT NULL,
      phone TEXT NOT NULL
    );
  `);
})();

// Middleware for error handling
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { error: err.message || 'Internal Server Error' };
  }
});

// Middleware for body parsing
app.use(bodyParser());

// Helper function to validate credit card and phone inputs
function validateInput(data, type) {
  if (type === 'credit_card') {
    const creditCardRegex = /^\d{16}$/; // Simple regex for 16-digit credit card numbers
    return creditCardRegex.test(data);
  } else if (type === 'phone') {
    const phoneRegex = /^[\d\-]+$/; // Simple regex for phone numbers (digits and dashes)
    return phoneRegex.test(data);
  }
  return false;
}

// Route to associate a credit card with a phone number
router.post('/associate_card', async (ctx) => {
  const { credit_card, phone } = ctx.request.body;

  // Input validation
  if (!credit_card || !phone) {
    ctx.status = 400;
    ctx.body = { error: 'Missing required fields: credit_card or phone' };
    return;
  }

  if (!validateInput(credit_card, 'credit_card')) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid credit card format' };
    return;
  }

  if (!validateInput(phone, 'phone')) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid phone format' };
    return;
  }

  // Insert into database
  try {
    await db.run(
      'INSERT INTO credit_card_associations (credit_card, phone) VALUES (?, ?)',
      [credit_card, phone]
    );
    ctx.status = 201;
    ctx.body = { message: 'Association created successfully' };
  } catch (err) {
    ctx.status = 500;
    ctx.body = { error: 'Failed to create association' };
  }
});

// Route to retrieve credit cards associated with a set of phone numbers
router.post('/retrieve_cards', async (ctx) => {
  const { phone_numbers } = ctx.request.body;

  // Input validation
  if (!phone_numbers || !Array.isArray(phone_numbers) || phone_numbers.length === 0) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid or missing phone_numbers array' };
    return;
  }

  for (const phone of phone_numbers) {
    if (!validateInput(phone, 'phone')) {
      ctx.status = 400;
      ctx.body = { error: `Invalid phone format: ${phone}` };
      return;
    }
  }

  // Query database for credit cards associated with all given phone numbers
  try {
    const placeholders = phone_numbers.map(() => '?').join(',');
    const query = `
      SELECT credit_card
      FROM credit_card_associations
      WHERE phone IN (${placeholders})
      GROUP BY credit_card
      HAVING COUNT(DISTINCT phone) = ?
    `;
    const cards = await db.all(query, [...phone_numbers, phone_numbers.length]);

    if (cards.length === 0) {
      ctx.status = 404;
      ctx.body = { error: 'No credit cards found for the given phone numbers' };
    } else {
      ctx.status = 200;
      ctx.body = { card_numbers: cards.map((row) => row.credit_card) };
    }
  } catch (err) {
    ctx.status = 500;
    ctx.body = { error: 'Failed to retrieve credit cards' };
  }
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});