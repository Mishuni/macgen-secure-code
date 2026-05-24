import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Initialize Fastify server
const app = fastify();

// Database setup
const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

async function setupDatabase() {
  const db = await dbPromise;
  await db.exec(`
    CREATE TABLE IF NOT EXISTS services (
      serviceId TEXT PRIMARY KEY,
      token TEXT NOT NULL,
      lastNotification TEXT NOT NULL
    )
  `);
}

// Define API Endpoints

// Register a heartbeat for a service
app.post('/heartbeat', async (request, reply) => {
  const { serviceId, token } = request.body;

  if (!serviceId || !token) {
    return reply.status(400).send({ error: 'Invalid request payload.' });
  }

  try {
    const db = await dbPromise;
    const now = new Date().toISOString();

    await db.run(`
      INSERT INTO services (serviceId, token, lastNotification)
      VALUES (?, ?, ?)
      ON CONFLICT(serviceId) DO UPDATE SET
      lastNotification=excluded.lastNotification
    `, [serviceId, token, now]);

    return reply.status(200).send({ message: 'Heartbeat registered successfully.' });
  } catch (error) {
    return reply.status(500).send({ error: 'Internal server error.' });
  }
});

// Get overview of registered services
app.post('/services', async (request, reply) => {
  const { token } = request.body;

  if (!token) {
    return reply.status(400).send({ error: 'Invalid request payload.' });
  }

  try {
    const db = await dbPromise;
    const services = await db.all(`
      SELECT serviceId, lastNotification
      FROM services
      WHERE token = ?
    `, [token]);

    return reply.status(200).send(services);
  } catch (error) {
    return reply.status(500).send({ error: 'Internal server error.' });
  }
});

// Start the server
const start = async () => {
  try {
    await setupDatabase();
    await app.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server listening on http://0.0.0.0:5000');
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

start();