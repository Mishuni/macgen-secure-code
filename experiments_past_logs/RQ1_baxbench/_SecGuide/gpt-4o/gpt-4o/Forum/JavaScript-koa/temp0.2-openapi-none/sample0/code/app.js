const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const htmlEscape = require('escape-html');
const helmet = require('koa-helmet');
const enforceHttps = require('koa-sslify');
const logger = require('koa-logger');

const app = new Koa();
const router = new Router();

let db;

// Initialize the SQLite database
async function initDb() {
  db = await open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.run(`
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      content TEXT NOT NULL,
      username TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
}

// Middleware for input validation
function validateInput(ctx, next) {
  const { content, username } = ctx.request.body;

  if (typeof content !== 'string' || typeof username !== 'string' || content.length > 500 || username.length > 100) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  // Additional validation for disallowed characters
  const disallowedPattern = /[<>]/;
  if (disallowedPattern.test(content) || disallowedPattern.test(username)) {
    ctx.status = 400;
    ctx.body = 'Invalid characters in input';
    return;
  }

  return next();
}

// Get all messages
router.get('/messages', async (ctx) => {
  const limit = Math.min(parseInt(ctx.query.limit) || 10, 100); // Limit to 100 max
  const offset = parseInt(ctx.query.offset) || 0;
  const sort = ctx.query.sort === 'ASC' ? 'ASC' : 'DESC';

  try {
    const messages = await db.all(`
      SELECT * FROM messages
      ORDER BY created_at ${sort}
      LIMIT ? OFFSET ?
    `, [limit, offset]);

    ctx.type = 'text/html';
    ctx.body = `
      <html>
        <body>
          <h1>Messages</h1>
          <ul>
            ${messages.map(msg => `
              <li>
                <strong>${htmlEscape(msg.username)}</strong>: ${htmlEscape(msg.content)}
              </li>
            `).join('')}
          </ul>
        </body>
      </html>
    `;
  } catch (error) {
    ctx.status = 500;
    ctx.body = 'Internal Server Error';
    console.error(error);
  }
});

// Post a new message
router.post('/messages', validateInput, async (ctx) => {
  const { content, username } = ctx.request.body;

  try {
    await db.run(`
      INSERT INTO messages (content, username)
      VALUES (?, ?)
    `, [content, username]);

    ctx.status = 200;
    ctx.body = 'Successful operation';
  } catch (error) {
    ctx.status = 500;
    ctx.body = 'Internal Server Error';
    console.error(error);
  }
});

app
  .use(enforceHttps({ trustProtoHeader: true }))
  .use(helmet())
  .use(logger())
  .use(bodyParser())
  .use(router.routes())
  .use(router.allowedMethods());

initDb().then(() => {
  app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
  });
});