const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');

dotenv.config();

const app = new Koa();
const router = new Router();

// Open the SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  // Create messages table if it doesn't exist
  await db.exec(`
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      content TEXT NOT NULL,
      username TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
})();

// Middleware
app.use(bodyParser());

// Routes
router.get('/messages', async (ctx) => {
  const limit = parseInt(ctx.query.limit) || 10;
  const offset = parseInt(ctx.query.offset) || 0;
  const sort = ctx.query.sort === 'ASC' ? 'ASC' : 'DESC';

  const messages = await db.all(
    `SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`,
    [limit, offset]
  );

  ctx.body = messages;
});

router.post('/messages', async (ctx) => {
  const { content, username } = ctx.request.body;

  if (!content || !username) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
    return;
  }

  await db.run(
    'INSERT INTO messages (content, username) VALUES (?, ?)',
    [content, username]
  );

  ctx.status = 200;
  ctx.body = { message: 'Message posted successfully' };
});

// Apply routes
app.use(router.routes()).use(router.allowedMethods());

// Error handling
app.on('error', (err, ctx) => {
  console.error('server error', err, ctx);
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});