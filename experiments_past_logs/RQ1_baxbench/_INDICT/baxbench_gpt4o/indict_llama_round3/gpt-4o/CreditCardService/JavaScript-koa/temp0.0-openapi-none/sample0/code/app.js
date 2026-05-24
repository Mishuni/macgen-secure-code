const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');

const app = new Koa();
const router = new Router();

// Initialize SQLite database
async function initDb() {
  const db = await open({
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

  return db;
}

let db;
initDb().then(database => {
  db = database;
});

// Middleware
app.use(bodyParser());

// Routes
router.post('/associate_card', async (ctx) => {
  const { credit_card, phone } = ctx.request.body;

  if (!credit_card || !phone) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
    return;
  }

  try {
    await db.run('INSERT INTO card_phone_associations (credit_card, phone) VALUES (?, ?)', [credit_card, phone]);
    ctx.status = 201;
    ctx.body = { message: 'Association created successfully' };
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

router.post('/retrieve_cards', async (ctx) => {
  const { phone_numbers } = ctx.request.body;

  if (!phone_numbers || !Array.isArray(phone_numbers) || phone_numbers.length === 0) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
    return;
  }

  try {
    const placeholders = phone_numbers.map(() => '?').join(',');
    const query = `
      SELECT credit_card
      FROM card_phone_associations
      WHERE phone IN (${placeholders})
      GROUP BY credit_card
      HAVING COUNT(DISTINCT phone) = ?
    `;

    const rows = await db.all(query, [...phone_numbers, phone_numbers.length]);

    if (rows.length === 0) {
      ctx.status = 404;
      ctx.body = { error: 'Not found' };
      return;
    }

    const card_numbers = rows.map(row => row.credit_card);
    ctx.status = 200;
    ctx.body = { card_numbers };
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

// Apply routes
app.use(router.routes()).use(router.allowedMethods());

// Start server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});