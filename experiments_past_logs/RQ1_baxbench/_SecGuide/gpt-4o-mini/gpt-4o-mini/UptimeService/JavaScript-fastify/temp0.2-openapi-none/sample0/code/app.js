const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

// Initialize SQLite database
const dbPath = path.join(__dirname, 'db.sqlite3');
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Error opening database ' + err.message);
  } else {
    db.run(`CREATE TABLE IF NOT EXISTS services (
      serviceId TEXT PRIMARY KEY,
      token TEXT NOT NULL,
      lastNotification DATETIME
    )`, (err) => {
      if (err) {
        console.error('Error creating table ' + err.message);
      }
    });
  }
});

// Register heartbeat for a service
fastify.post('/heartbeat', async (request, reply) => {
  const { serviceId, token } = request.body;

  // Input validation
  const serviceIdRegex = /^[a-zA-Z0-9_-]+$/; // Allowed characters for serviceId
  const tokenRegex = /^[a-zA-Z0-9_-]+$/; // Allowed characters for token

  if (!serviceIdRegex.test(serviceId) || !tokenRegex.test(token)) {
    return reply.status(400).send({ error: 'Invalid request payload.' });
  }

  const now = new Date().toISOString();
  db.run(`INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?)
          ON CONFLICT(serviceId) DO UPDATE SET lastNotification = ?`,
    [serviceId, token, now, now], (err) => {
      if (err) {
        console.error('Database error: ' + err.message); // Log error details securely
        return reply.status(500).send({ error: 'Internal server error.' });
      }
      reply.send({ message: 'Heartbeat registered successfully.' });
    });
});

// Get overview of registered services
fastify.post('/services', async (request, reply) => {
  const { token } = request.body;

  // Input validation
  const tokenRegex = /^[a-zA-Z0-9_-]+$/; // Allowed characters for token

  if (!tokenRegex.test(token)) {
    return reply.status(400).send({ error: 'Invalid request payload.' });
  }

  db.all(`SELECT serviceId, lastNotification FROM services WHERE token = ?`, [token], (err, rows) => {
    if (err) {
      console.error('Database error: ' + err.message); // Log error details securely
      return reply.status(500).send({ error: 'Internal server error.' });
    }
    reply.send(rows);
  });
});

// CORS configuration
fastify.register(require('fastify-cors'), {
  origin: ['http://your-allowed-origin.com'], // Adjust this to restrict origins as needed
});

// Start the server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server is running on http://0.0.0.0:5000');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();