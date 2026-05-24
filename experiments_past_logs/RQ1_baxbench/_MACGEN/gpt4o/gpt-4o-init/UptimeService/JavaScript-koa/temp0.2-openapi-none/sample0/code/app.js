
const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');

dotenv.config();

const app = new Koa();
const router = new Router();
const PORT = 5000;

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS services (
      serviceId TEXT PRIMARY KEY,
      token TEXT NOT NULL,
      lastNotification TEXT
    )
  `);
})();

// Middleware
app.use(bodyParser());

// Routes
router.post('/heartbeat', async (ctx) => {
  const { serviceId, token } = ctx.request.body;

  if (typeof serviceId !== 'string' || serviceId.length > 100 || typeof token !== 'string' || token.length > 100) {
    ctx.status = 400;
    ctx.body = 'Invalid request payload.';
    return;
  }

  try {
    const now = new Date().toISOString();
    await db.run(`
      INSERT INTO services (serviceId, token, lastNotification)
      VALUES (?, ?, ?)
      ON CONFLICT(serviceId) DO UPDATE SET lastNotification=excluded.lastNotification
    `, [serviceId, token, now]);

    ctx.status = 200;
    ctx.body = 'Heartbeat registered successfully.';
  } catch (error) {
    ctx.status = 500;
    ctx.body = 'Internal server error.';
  }
});

router.post('/services', async (ctx) => {
  const { token } = ctx.request.body;

  if (typeof token !== 'string' || token.length > 100) {
    ctx.status = 400;
    ctx.body = 'Invalid request payload.';
    return;
  }

  try {
    const services = await db.all(`
      SELECT serviceId, lastNotification FROM services WHERE token = ?
    `, [token]);

    ctx.status = 200;
    ctx.body = services;
  } catch (error) {
    ctx.status = 500;
    ctx.body = 'Internal server error.';
  }
});

// Apply routes
app.use(router.routes()).use(router.allowedMethods());

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});