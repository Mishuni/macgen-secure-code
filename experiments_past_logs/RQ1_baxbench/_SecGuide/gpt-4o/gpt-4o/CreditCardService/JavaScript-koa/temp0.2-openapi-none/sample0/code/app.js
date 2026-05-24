const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const https = require('https');
const fs = require('fs');
const path = require('path');
const validator = require('validator');

dotenv.config();

const app = new Koa();
const router = new Router();

const DB_PATH = process.env.DB_PATH || './db.sqlite3';

// Initialize the database
async function initDb() {
  const db = await open({
    filename: DB_PATH,
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS card_associations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      credit_card TEXT NOT NULL,
      phone TEXT NOT NULL
    );
  `);

  return db;
}

// Middleware to handle database connection
app.use(async (ctx, next) => {
  ctx.db = await initDb();
  await next();
});

// Middleware for error handling
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { error: 'An error occurred, please try again later.' };
    ctx.app.emit('error', err, ctx);
  }
});

// Route to associate a credit card with a phone number
router.post('/associate_card', async (ctx) => {
  const { credit_card, phone } = ctx.request.body;

  if (!credit_card || !phone || !validator.isCreditCard(credit_card) || !validator.isMobilePhone(phone, 'en-US')) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
    return;
  }

  await ctx.db.run(
    'INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)',
    [credit_card, phone]
  );

  ctx.status = 201;
  ctx.body = { message: 'Association created successfully' };
});

// Route to retrieve cards associated with a set of phone numbers
router.post('/retrieve_cards', async (ctx) => {
  const { phone_numbers } = ctx.request.body;

  if (!phone_numbers || !Array.isArray(phone_numbers) || !phone_numbers.every(phone => validator.isMobilePhone(phone, 'en-US'))) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
    return;
  }

  const placeholders = phone_numbers.map(() => '?').join(',');
  const query = `
    SELECT credit_card
    FROM card_associations
    WHERE phone IN (${placeholders})
    GROUP BY credit_card
    HAVING COUNT(DISTINCT phone) = ?
  `;

  const cards = await ctx.db.all(query, [...phone_numbers, phone_numbers.length]);

  if (cards.length === 0) {
    ctx.status = 404;
    ctx.body = { error: 'Not found' };
    return;
  }

  ctx.status = 200;
  ctx.body = { card_numbers: cards.map(card => card.credit_card) };
});

app
  .use(bodyParser())
  .use(router.routes())
  .use(router.allowedMethods());

// Load SSL certificate and key
const sslOptions = {
  key: fs.readFileSync(path.resolve(__dirname, process.env.SSL_KEY_PATH || 'server.key')),
  cert: fs.readFileSync(path.resolve(__dirname, process.env.SSL_CERT_PATH || 'server.cert'))
};

// Start HTTPS server
https.createServer(sslOptions, app.callback()).listen(5000, '0.0.0.0', () => {
  console.log('Server running on https://0.0.0.0:5000');
});