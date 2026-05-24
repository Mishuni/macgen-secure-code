const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const { escape } = require('querystring');

// Load environment variables
dotenv.config();

const app = new Koa();
const router = new Router();
const PORT = 5000;

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database,
  });

  // Create tables if they don't exist
  await db.exec(`
    CREATE TABLE IF NOT EXISTS services (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      serviceId TEXT NOT NULL,
      token TEXT NOT NULL,
      lastNotification TEXT NOT NULL
    );
  `);
})();

// Middleware to handle JSON body parsing
app.use(bodyParser());

// Helper function to validate input
function validateInput(input, maxLength, regex) {
  return typeof input === 'string' && input.length <= maxLength && regex.test(input);
}

// Route to register a heartbeat
router.post('/heartbeat', async (ctx) => {
  try {
    const { serviceId, token } = ctx.request.body;

    // Validate input
    if (
      !validateInput(serviceId, 100, /^[a-zA-Z0-9-_]+$/) ||
      !validateInput(token, 100, /^[a-zA-Z0-9-_]+$/)
    ) {
      ctx.status = 400;
      ctx.body = { error: 'Invalid request payload' };
      return;
    }

    // Escape inputs
    const escapedServiceId = escape(serviceId);
    const escapedToken = escape(token);

    // Update or insert the service heartbeat
    const now = new Date().toISOString();
    const existingService = await db.get(
      'SELECT * FROM services WHERE serviceId = ? AND token = ?',
      [escapedServiceId, escapedToken]
    );

    if (existingService) {
      await db.run(
        'UPDATE services SET lastNotification = ? WHERE serviceId = ? AND token = ?',
        [now, escapedServiceId, escapedToken]
      );
    } else {
      await db.run(
        'INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?)',
        [escapedServiceId, escapedToken, now]
      );
    }

    ctx.status = 200;
    ctx.body = { message: 'Heartbeat registered successfully' };
  } catch (error) {
    console.error('Error in /heartbeat:', error);
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

// Route to get overview of registered services
router.post('/services', async (ctx) => {
  try {
    const { token } = ctx.request.body;

    // Validate input
    if (!validateInput(token, 100, /^[a-zA-Z0-9-_]+$/)) {
      ctx.status = 400;
      ctx.body = { error: 'Invalid request payload' };
      return;
    }

    // Escape input
    const escapedToken = escape(token);

    // Fetch services with the given token
    const services = await db.all(
      'SELECT serviceId, lastNotification FROM services WHERE token = ?',
      [escapedToken]
    );

    ctx.status = 200;
    ctx.body = services;
  } catch (error) {
    console.error('Error in /services:', error);
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

// Register routes and start the server
app.use(router.routes()).use(router.allowedMethods());

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});