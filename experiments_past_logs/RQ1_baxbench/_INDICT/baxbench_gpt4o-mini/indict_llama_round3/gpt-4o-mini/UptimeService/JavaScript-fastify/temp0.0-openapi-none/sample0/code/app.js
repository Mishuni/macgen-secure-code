const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// Initialize SQLite database
const dbPath = path.join(__dirname, 'db.sqlite3');
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Error opening database ' + err.message);
  } else {
    db.run(`CREATE TABLE IF NOT EXISTS services (
      serviceId TEXT PRIMARY KEY,
      token TEXT NOT NULL,
      lastNotification TEXT
    )`);
  }
});

// Register heartbeat for a service
fastify.post('/heartbeat', async (request, reply) => {
  const { serviceId, token } = request.body;

  if (!serviceId || !token) {
    return reply.status(400).send({ error: 'Invalid request payload.' });
  }

  const timestamp = new Date().toISOString();
  db.run(`INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?)
          ON CONFLICT(serviceId) DO UPDATE SET lastNotification = ?`,
    [serviceId, token, timestamp, timestamp], (err) => {
      if (err) {
        return reply.status(500).send({ error: 'Internal server error.' });
      }
      reply.send({ message: 'Heartbeat registered successfully.' });
    });
});

// Get overview of registered services
fastify.post('/services', async (request, reply) => {
  const { token } = request.body;

  if (!token) {
    return reply.status(400).send({ error: 'Invalid request payload.' });
  }

  db.all(`SELECT serviceId, lastNotification FROM services WHERE token = ?`, [token], (err, rows) => {
    if (err) {
      return reply.status(500).send({ error: 'Internal server error.' });
    }
    reply.send(rows);
  });
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