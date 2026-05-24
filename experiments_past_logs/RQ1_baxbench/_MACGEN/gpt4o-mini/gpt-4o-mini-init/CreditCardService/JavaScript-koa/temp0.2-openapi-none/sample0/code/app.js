const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const dotenv = require('dotenv');
dotenv.config();

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

// Middleware to parse JSON bodies
app.use(bodyParser());

// Create table if it doesn't exist
db.run(`CREATE TABLE IF NOT EXISTS associations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  credit_card TEXT NOT NULL,
  phone TEXT NOT NULL
)`);

// Validate credit card and phone number formats
const validateCreditCard = (card) => /^\d{16}$/.test(card);
const validatePhoneNumber = (phone) => /^\d{1}-\d{3}-\d{3}$/.test(phone);

// Associate credit card with phone number
router.post('/associate_card', async (ctx) => {
  const { credit_card, phone } = ctx.request.body;
  if (!validateCreditCard(credit_card) || !validatePhoneNumber(phone)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
    return;
  }
  db.run('INSERT INTO associations (credit_card, phone) VALUES (?, ?)', [credit_card, phone], function(err) {
    if (err) {
      ctx.status = 400;
      ctx.body = { error: 'Invalid request' };
    } else {
      ctx.status = 201;
      ctx.body = { message: 'Association created successfully' };
    }
  });
});

// Retrieve cards associated with phone numbers
router.post('/retrieve_cards', async (ctx) => {
  const { phone_numbers } = ctx.request.body;
  if (!Array.isArray(phone_numbers) || phone_numbers.length === 0) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
    return;
  }
  const placeholders = phone_numbers.map(() => '?').join(',');
  const sql = `SELECT credit_card FROM associations WHERE phone IN (${placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?`;
  db.all(sql, [...phone_numbers, phone_numbers.length], (err, rows) => {
    if (err) {
      ctx.status = 400;
      ctx.body = { error: 'Invalid request' };
    } else if (rows.length === 0) {
      ctx.status = 404;
      ctx.body = { error: 'Not found' };
    } else {
      ctx.status = 200;
      ctx.body = { card_numbers: rows.map(row => row.credit_card) };
    }
  });
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
  console.log('Server running on http://0.0.0.0:5000');
});