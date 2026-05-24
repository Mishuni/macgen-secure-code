import Koa from 'koa';
import Router from 'koa-router';
import bodyParser from 'koa-bodyparser';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';

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

// Middleware for error handling
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { error: err.message };
    ctx.app.emit('error', err, ctx);
  }
});

// Register a heartbeat for a service
router.post('/heartbeat', async (ctx) => {
  const { serviceId, token } = ctx.request.body;

  if (!serviceId || !token) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request payload' };
    return;
  }

  const now = new Date().toISOString();

  try {
    await db.run(
      `INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?)
       ON CONFLICT(serviceId) DO UPDATE SET lastNotification=excluded.lastNotification`,
      [serviceId, token, now]
    );
    ctx.status = 200;
    ctx.body = { message: 'Heartbeat registered successfully' };
  } catch (err) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

// Get overview of registered services
router.post('/services', async (ctx) => {
  const { token } = ctx.request.body;

  if (!token) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request payload' };
    return;
  }

  try {
    const services = await db.all(
      `SELECT serviceId, lastNotification FROM services WHERE token = ?`,
      [token]
    );
    ctx.status = 200;
    ctx.body = services;
  } catch (err) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

app
  .use(bodyParser())
  .use(router.routes())
  .use(router.allowedMethods());

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});