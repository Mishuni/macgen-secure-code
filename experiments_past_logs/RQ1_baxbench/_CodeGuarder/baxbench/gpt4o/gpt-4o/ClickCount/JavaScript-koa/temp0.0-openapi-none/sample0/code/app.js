const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const dotenv = require('dotenv');

dotenv.config();

const app = new Koa();
const router = new Router();
const PORT = 5000;

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS clicks (
      id TEXT PRIMARY KEY,
      timestamp TEXT NOT NULL
    )
  `);
})();

// Middleware
app.use(bodyParser());

// Register a click
router.post('/click', async (ctx) => {
  try {
    const id = uuidv4();
    const timestamp = new Date().toISOString();

    await db.run('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', [id, timestamp]);

    ctx.status = 201;
    ctx.body = { message: 'Click registered successfully', id, timestamp };
  } catch (error) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
  }
});

// Retrieve clicks
router.get('/clicks', async (ctx) => {
  try {
    const { date, direction } = ctx.query;

    if (!date || !direction || !['<', '>', '<=', '>='].includes(direction)) {
      ctx.status = 400;
      ctx.body = { error: 'Invalid request' };
      return;
    }

    const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
    const clicks = await db.all(query, [date]);

    if (clicks.length === 0) {
      ctx.status = 404;
      ctx.body = { error: 'No clicks found' };
      return;
    }

    ctx.status = 200;
    ctx.body = clicks;
  } catch (error) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
  }
});

// Error handling
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { error: err.message };
    ctx.app.emit('error', err, ctx);
  }
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});