const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { config } = require('dotenv');
const cors = require('@koa/cors');

config();

const app = new Koa();
const router = new Router();
const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

// Middleware to handle errors
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { error: 'Internal Server Error' };
    // Log the error securely (consider using a logging service in production)
    console.error(err.message);
  }
});

// Initialize database
const initDb = async () => {
  const db = await dbPromise;
  await db.exec(`
    CREATE TABLE IF NOT EXISTS clicks (
      id TEXT PRIMARY KEY,
      timestamp TEXT NOT NULL
    )
  `);
};

// Validate timestamp format (ISO 8601)
const isValidTimestamp = (timestamp) => {
  const iso8601Regex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
  return iso8601Regex.test(timestamp);
};

// Validate ID format (alphanumeric)
const isValidId = (id) => {
  const idRegex = /^[a-zA-Z0-9]+$/; // Adjust regex as needed for your ID format
  return idRegex.test(id);
};

// Register a click
router.post('/click', async (ctx) => {
  const { id, timestamp } = ctx.request.body;

  if (!id || !timestamp || !isValidId(id) || !isValidTimestamp(timestamp)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
    return;
  }

  const db = await dbPromise;
  await db.run('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', [id, timestamp]);
  ctx.status = 201;
});

// Retrieve clicks
router.get('/clicks', async (ctx) => {
  const { date, direction } = ctx.query;

  if (!date || !direction) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
    return;
  }

  const validDirections = ['<', '>', '<=', '>='];
  if (!validDirections.includes(direction)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid direction' };
    return;
  }

  const db = await dbPromise;
  const clicks = await db.all(`SELECT * FROM clicks WHERE timestamp ${direction} ?`, [date]);

  if (clicks.length === 0) {
    ctx.status = 404;
    ctx.body = { error: 'No clicks found' };
    return;
  }

  ctx.status = 200;
  ctx.body = clicks;
});

// Setup the app
app.use(cors()); // Enable CORS
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server
const startServer = async () => {
  await initDb();
  app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
  });
};

startServer();