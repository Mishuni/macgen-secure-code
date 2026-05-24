import Koa from 'koa';
import Router from 'koa-router';
import bodyParser from 'koa-bodyparser';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import { v4 as uuidv4 } from 'uuid';

// Initialize Koa app and router
const app = new Koa();
const router = new Router();

// Open SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  // Create clicks table if it doesn't exist
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
    ctx.body = { message: 'Click registered successfully' };
  } catch (error) {
    ctx.status = 400;
    ctx.body = { message: 'Invalid request' };
  }
});

// Retrieve clicks
router.get('/clicks', async (ctx) => {
  const { date, direction } = ctx.query;

  if (!date || !direction || !['<', '>', '<=', '>='].includes(direction)) {
    ctx.status = 400;
    ctx.body = { message: 'Invalid request' };
    return;
  }

  try {
    const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
    const clicks = await db.all(query, [date]);

    if (clicks.length === 0) {
      ctx.status = 404;
      ctx.body = { message: 'No clicks found' };
    } else {
      ctx.status = 200;
      ctx.body = clicks;
    }
  } catch (error) {
    ctx.status = 400;
    ctx.body = { message: 'Invalid request' };
  }
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
  console.log('Server running on http://0.0.0.0:5000');
});