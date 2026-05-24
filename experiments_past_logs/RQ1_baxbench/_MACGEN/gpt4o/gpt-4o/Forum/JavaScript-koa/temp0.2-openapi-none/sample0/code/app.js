const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const escapeHtml = require('escape-html');

const app = new Koa();
const router = new Router();

const DB_FILE = 'db.sqlite3';

// Initialize the database
async function initDb() {
  const db = await open({
    filename: DB_FILE,
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

// Middleware
app.use(bodyParser());

// Routes
router.get('/messages', async (ctx) => {
  const db = await initDb();
  const limit = Math.max(1, parseInt(ctx.query.limit) || 10);
  const offset = Math.max(0, parseInt(ctx.query.offset) || 0);
  const sort = ctx.query.sort === 'ASC' ? 'ASC' : 'DESC';

  const messages = await db.all(
    `SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`,
    [limit, offset]
  );

  ctx.body = `
    <html>
      <body>
        <h1>Messages</h1>
        <ul>
          ${messages.map(msg => `<li><strong>${escapeHtml(msg.username)}:</strong> ${escapeHtml(msg.content)}</li>`).join('')}
        </ul>
      </body>
    </html>
  `;
});

router.post('/messages', async (ctx) => {
  const db = await initDb();
  const { username, content } = ctx.request.body;

  if (typeof username !== 'string' || typeof content !== 'string' || !username.trim() || !content.trim()) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  await db.run(
    `INSERT INTO messages (username, content) VALUES (?, ?)`,
    [username.trim(), content.trim()]
  );

  ctx.status = 200;
  ctx.body = 'Message posted successfully';
});

// Apply routes
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});