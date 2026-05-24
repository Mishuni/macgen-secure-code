const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const helmet = require('koa-helmet');
const cors = require('@koa/cors');

const app = new Koa();
const router = new Router();

// Open the SQLite database
let db;
(async () => {
  try {
    db = await open({
      filename: './db.sqlite3',
      driver: sqlite3.Database
    });

    // Create the clicks table if it doesn't exist
    await db.exec(`
      CREATE TABLE IF NOT EXISTS clicks (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL
      )
    `);
  } catch (error) {
    console.error('Failed to open database:', error);
    process.exit(1);
  }
})();

// Middleware
app.use(helmet());
app.use(cors());
app.use(bodyParser());

// Helper function to validate ISO 8601 date format
function isValidISODate(date) {
  const isoDateRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$/;
  return isoDateRegex.test(date);
}

// Register a click
router.post('/click', async (ctx) => {
  try {
    const id = uuidv4();
    const timestamp = new Date().toISOString();

    await db.run('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', [id, timestamp]);

    ctx.status = 201;
    ctx.body = { message: 'Click registered successfully' };
  } catch (error) {
    console.error('Error registering click:', error);
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

// Retrieve clicks
router.get('/clicks', async (ctx) => {
  const { date, direction } = ctx.query;

  if (!date || !direction || !['<', '>', '<=', '>='].includes(direction) || !isValidISODate(date)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
    return;
  }

  try {
    const query = `SELECT * FROM clicks WHERE timestamp ${direction} ? LIMIT 100`; // Added pagination limit
    const clicks = await db.all(query, [date]);

    if (clicks.length === 0) {
      ctx.status = 404;
      ctx.body = { error: 'No clicks found' };
    } else {
      ctx.status = 200;
      ctx.body = clicks;
    }
  } catch (error) {
    console.error('Error retrieving clicks:', error);
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});