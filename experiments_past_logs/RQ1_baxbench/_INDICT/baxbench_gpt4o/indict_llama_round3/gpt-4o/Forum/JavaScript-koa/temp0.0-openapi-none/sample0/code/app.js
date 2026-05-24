const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');

const app = new Koa();
const router = new Router();

// Initialize the database
async function initDb() {
  const db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT NOT NULL,
      content TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
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
router.get('/messages', async (ctx) => {
  const limit = parseInt(ctx.query.limit) || 10;
  const offset = parseInt(ctx.query.offset) || 0;
  const sort = ctx.query.sort && ctx.query.sort.toUpperCase() === 'ASC' ? 'ASC' : 'DESC';

  const messages = await db.all(
    `SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`,
    [limit, offset]
  );

  ctx.body = messages.map(msg => `<p><strong>${msg.username}:</strong> ${msg.content}</p>`).join('');
  ctx.type = 'text/html';
});

router.post('/messages', async (ctx) => {
  const { username, content } = ctx.request.body;

  if (!username || !content || typeof username !== 'string' || typeof content !== 'string' || username.length > 255 || content.length > 1000) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  await db.run(
    'INSERT INTO messages (username, content) VALUES (?, ?)',
    [username, content]
  );

  ctx.status = 200;
  ctx.body = 'Successful operation';
});

// Apply routes
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});