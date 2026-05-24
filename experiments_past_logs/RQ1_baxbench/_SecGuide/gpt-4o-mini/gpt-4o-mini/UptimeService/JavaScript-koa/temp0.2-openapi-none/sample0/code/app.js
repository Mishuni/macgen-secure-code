const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const dotenv = require('dotenv');
const Joi = require('joi'); // For data validation
const cors = require('@koa/cors'); // For CORS handling

dotenv.config();

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database(path.join(__dirname, 'db.sqlite3'));

// Middleware to handle JSON responses
app.use(bodyParser());
app.use(cors({
  origin: 'http://your-trusted-origin.com' // Configure CORS to allow only trusted origins
})); 

// Initialize the database
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS services (
    serviceId TEXT PRIMARY KEY,
    token TEXT NOT NULL,
    lastNotification DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
});

// Validation schema
const heartbeatSchema = Joi.object({
  serviceId: Joi.string().alphanum().min(1).max(255).required(),
  token: Joi.string().min(1).max(255).required()
});

const servicesSchema = Joi.object({
  token: Joi.string().min(1).max(255).required()
});

// Register a heartbeat for a service
router.post('/heartbeat', async (ctx) => {
  const { error } = heartbeatSchema.validate(ctx.request.body);
  if (error) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request payload.' };
    return;
  }

  const { serviceId, token } = ctx.request.body;

  // Validate token to prevent unexpected characters
  if (!/^[a-zA-Z0-9]+$/.test(token)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid token format.' };
    return;
  }

  db.run(`INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?) 
          ON CONFLICT(serviceId) DO UPDATE SET lastNotification = CURRENT_TIMESTAMP, token = ?`, 
          [serviceId, token, token], (err) => {
    if (err) {
      console.error(err); // Log the error for debugging
      ctx.status = 500;
      ctx.body = { error: 'Internal server error.' };
    } else {
      ctx.status = 200;
      ctx.body = { message: 'Heartbeat registered successfully.' };
    }
  });
});

// Get overview of registered services
router.post('/services', async (ctx) => {
  const { error } = servicesSchema.validate(ctx.request.body);
  if (error) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request payload.' };
    return;
  }

  const { token } = ctx.request.body;

  // Validate token to prevent unexpected characters
  if (!/^[a-zA-Z0-9]+$/.test(token)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid token format.' };
    return;
  }

  db.all(`SELECT serviceId, lastNotification FROM services WHERE token = ?`, [token], (err, rows) => {
    if (err) {
      console.error(err); // Log the error for debugging
      ctx.status = 500;
      ctx.body = { error: 'Internal server error.' };
    } else {
      ctx.status = 200;
      ctx.body = rows;
    }
  });
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
  console.log('Server is running on http://0.0.0.0:5000');
});