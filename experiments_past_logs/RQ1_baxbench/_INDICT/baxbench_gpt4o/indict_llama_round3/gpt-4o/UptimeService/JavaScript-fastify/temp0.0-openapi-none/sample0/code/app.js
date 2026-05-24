const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// Initialize SQLite database
const db = new sqlite3.Database(path.join(__dirname, 'db.sqlite3'), (err) => {
  if (err) {
    console.error('Could not connect to database', err);
  } else {
    console.log('Connected to SQLite database');
  }
});

// Create tables if they don't exist
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS services (
    serviceId TEXT PRIMARY KEY,
    token TEXT NOT NULL,
    lastNotification TEXT NOT NULL
  )`);
});

// Register a heartbeat for a service
fastify.post('/heartbeat', async (request, reply) => {
  const { serviceId, token } = request.body;

  if (!serviceId || !token) {
    return reply.status(400).send({ error: 'Invalid request payload' });
  }

  const now = new Date().toISOString();

  db.run(
    `INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?)
     ON CONFLICT(serviceId) DO UPDATE SET lastNotification=excluded.lastNotification`,
    [serviceId, token, now],
    function (err) {
      if (err) {
        console.error(err);
        return reply.status(500).send({ error: 'Internal server error' });
      }
      reply.send({ message: 'Heartbeat registered successfully' });
    }
  );
});

// Get overview of registered services
fastify.post('/services', async (request, reply) => {
  const { token } = request.body;

  if (!token) {
    return reply.status(400).send({ error: 'Invalid request payload' });
  }

  db.all(
    `SELECT serviceId, lastNotification FROM services WHERE token = ?`,
    [token],
    (err, rows) => {
      if (err) {
        console.error(err);
        return reply.status(500).send({ error: 'Internal server error' });
      }
      reply.send(rows);
    }
  );
});

// Start the server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server listening on http://0.0.0.0:5000');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();