const fastify = require('fastify')({ logger: { level: 'info' } });
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const dotenv = require('dotenv');

dotenv.config();

const APP_SECRET = process.env.APP_SECRET;
if (!APP_SECRET) {
  throw new Error('APP_SECRET environment variable is required');
}

let db;

// Initialize SQLite database
async function initDb() {
  db = await sqlite.open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.run(`
    CREATE TABLE IF NOT EXISTS services (
      serviceId TEXT PRIMARY KEY,
      token TEXT NOT NULL,
      lastNotification TEXT NOT NULL
    )
  `);
}

// Register a heartbeat for a service
fastify.post('/heartbeat', async (request, reply) => {
  const { serviceId, token } = request.body;

  if (!serviceId || !token || typeof serviceId !== 'string' || typeof token !== 'string') {
    return reply.status(400).send({ error: 'Invalid request payload.' });
  }

  try {
    const now = new Date().toISOString();
    await db.run(`
      INSERT INTO services (serviceId, token, lastNotification)
      VALUES (?, ?, ?)
      ON CONFLICT(serviceId) DO UPDATE SET lastNotification=excluded.lastNotification
    `, [serviceId, token, now]);

    return reply.status(200).send({ message: 'Heartbeat registered successfully.' });
  } catch (error) {
    request.log.error(error);
    return reply.status(500).send({ error: 'Internal server error.' });
  }
});

// Get overview of registered services
fastify.post('/services', async (request, reply) => {
  const { token } = request.body;

  if (!token || typeof token !== 'string') {
    return reply.status(400).send({ error: 'Invalid request payload.' });
  }

  try {
    const services = await db.all(`
      SELECT serviceId, lastNotification FROM services WHERE token = ?
    `, [token]);

    return reply.status(200).send(services);
  } catch (error) {
    request.log.error(error);
    return reply.status(500).send({ error: 'Internal server error.' });
  }
});

// Start the server
const start = async () => {
  try {
    await initDb();
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();