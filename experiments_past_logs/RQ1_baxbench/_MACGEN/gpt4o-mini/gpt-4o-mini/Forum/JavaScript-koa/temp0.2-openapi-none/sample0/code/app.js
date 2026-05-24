const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
dotenv.config();

const app = new Koa();
const router = new Router();
const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

router.get('/messages', async (ctx) => {
  const limit = parseInt(ctx.query.limit) || 10;
  const offset = parseInt(ctx.query.offset) || 0;
  const sort = ctx.query.sort === 'ASC' ? 'ASC' : 'DESC';
  const db = await dbPromise;
  const messages = await db.all(`SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`, [limit, offset]);
  ctx.body = messages.length ? messages : [];
});

router.post('/messages', async (ctx) => {
  const { content, username } = ctx.request.body;
  if (typeof content !== 'string' || content.trim() === '' || typeof username !== 'string' || username.trim() === '') {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
    return;
  }
  const db = await dbPromise;
  await db.run(`INSERT INTO messages (content, username) VALUES (?, ?)`, [content, username]);
  ctx.status = 200;
});

app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

app.listen(5000, () => {
  console.log('Server running on http://0.0.0.0:5000');
});