const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const app = new Koa();
const router = new Router();
const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

async function initDb() {
  const db = await dbPromise;
  await db.exec(`CREATE TABLE IF NOT EXISTS clicks (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL
  )`);
}

app.use(bodyParser());

router.post('/click', async (ctx) => {
  const db = await dbPromise;
  const click = {
    id: uuidv4(),
    timestamp: new Date().toISOString()
  };

  await db.run('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', [click.id, click.timestamp]);
  ctx.status = 201;
  ctx.body = { id: click.id, timestamp: click.timestamp };
});

router.get('/clicks', async (ctx) => {
  const { date, direction } = ctx.query;

  const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
  if (!date || !dateRegex.test(date) || !direction || !['<', '>', '<=', '>='].includes(direction)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
    return;
  }

  const operator = direction;
  const clicks = await db.all(`SELECT * FROM clicks WHERE timestamp ${operator} ?`, [date]);

  if (clicks.length === 0) {
    ctx.status = 404;
    ctx.body = { error: 'No clicks found' };
  } else {
    ctx.status = 200;
    ctx.body = clicks.map(click => ({ id: click.id, timestamp: click.timestamp }));
  }
});

app.use(router.routes()).use(router.allowedMethods());

initDb().then(() => {
  app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
  });
});