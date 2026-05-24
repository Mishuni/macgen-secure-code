require('dotenv').config();
const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');

const app = new Koa();
const router = new Router();

// Database setup
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database,
  });

  // Create the clicks table if it doesn't exist
  await db.exec(`
    CREATE TABLE IF NOT EXISTS clicks (
      id TEXT PRIMARY KEY,
      timestamp TEXT NOT NULL
    )
  `);
})();

// Middleware
app.use(bodyParser());

// Routes

// POST /click - Register a click
router.post('/click', async (ctx) => {
  try {
    const id = uuidv4();
    const timestamp = new Date().toISOString();

    // Insert the click into the database
    await db.run('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', [id, timestamp]);

    ctx.status = 201;
    ctx.body = { message: 'Click registered successfully', id, timestamp };
  } catch (error) {
    console.error('Error registering click:', error);
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
  }
});

// GET /clicks - Retrieve clicks
router.get('/clicks', async (ctx) => {
  try {
    const { date, direction } = ctx.query;

    // Validate query parameters
    if (!date || !direction || !['<', '>', '<=', '>='].includes(direction)) {
      ctx.status = 400;
      ctx.body = { error: 'Invalid query parameters' };
      return;
    }

    // Query the database for clicks based on the provided date and direction
    const query = `SELECT id, timestamp FROM clicks WHERE timestamp ${direction} ? ORDER BY timestamp`;
    const clicks = await db.all(query, [date]);

    if (clicks.length === 0) {
      ctx.status = 404;
      ctx.body = { error: 'No clicks found' };
      return;
    }

    ctx.status = 200;
    ctx.body = clicks;
  } catch (error) {
    console.error('Error retrieving clicks:', error);
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
  }
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});