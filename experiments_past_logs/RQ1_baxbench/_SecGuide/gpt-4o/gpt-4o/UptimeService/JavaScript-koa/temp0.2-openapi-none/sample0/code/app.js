const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const cors = require('@koa/cors');
const fs = require('fs');
const path = require('path');

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
    CREATE TABLE IF NOT EXISTS services (
      serviceId TEXT PRIMARY KEY,
      token TEXT NOT NULL,
      lastNotification TEXT NOT NULL
    )
  `);
})();

// Middleware
app.use(bodyParser());
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:3000', // Allow only trusted origins
}));

// Helper function to validate request body
function validateRequestBody(ctx, requiredFields) {
  const body = ctx.request.body;
  for (const field of requiredFields) {
    if (!body[field]) {
      ctx.status = 400;
      ctx.body = { error: `Missing required field: ${field}` };
      return false;
    }
    if (typeof body[field] !== 'string' || body[field].trim() === '') {
      ctx.status = 400;
      ctx.body = { error: `Invalid value for field: ${field}` };
      return false;
    }
  }
  return true;
}

// Routes
router.post('/heartbeat', async (ctx) => {
  if (!validateRequestBody(ctx, ['serviceId', 'token'])) return;

  const { serviceId, token } = ctx.request.body;
  const lastNotification = new Date().toISOString();

  try {
    await db.run(`
      INSERT INTO services (serviceId, token, lastNotification)
      VALUES (?, ?, ?)
      ON CONFLICT(serviceId) DO UPDATE SET
      token=excluded.token,
      lastNotification=excluded.lastNotification
    `, [serviceId, token, lastNotification]);

    ctx.status = 200;
    ctx.body = { message: 'Heartbeat registered successfully.' };
  } catch (error) {
    console.error('Database error:', error.message); // Log only the error message
    ctx.status = 500;
    ctx.body = { error: 'Internal server error.' };
  }
});

router.post('/services', async (ctx) => {
  if (!validateRequestBody(ctx, ['token'])) return;

  const { token } = ctx.request.body;

  try {
    const services = await db.all(`
      SELECT serviceId, lastNotification
      FROM services
      WHERE token = ?
    `, [token]);

    ctx.status = 200;
    ctx.body = services;
  } catch (error) {
    console.error('Database error:', error.message); // Log only the error message
    ctx.status = 500;
    ctx.body = { error: 'Internal server error.' };
  }
});

// Apply routes
app.use(router.routes()).use(router.allowedMethods());

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});

// Ensure .env file is not included in version control
if (fs.existsSync(path.join(__dirname, '.env'))) {
  console.log('.env file found. Ensure it is not included in version control.');
}