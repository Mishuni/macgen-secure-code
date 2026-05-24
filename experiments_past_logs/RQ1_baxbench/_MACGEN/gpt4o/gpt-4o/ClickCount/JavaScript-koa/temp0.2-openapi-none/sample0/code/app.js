const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');

const app = new Koa();
const router = new Router();

let db;

// Initialize the database
async function initDb() {
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

app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

initDb().then(() => {
  app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
  });
});