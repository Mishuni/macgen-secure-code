import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

// Initialize Fastify server
const app = fastify();

// Configure SQLite Database
let db;
(async () => {
  db = await open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS clicks (
      id TEXT PRIMARY KEY,
      timestamp TEXT NOT NULL
    )
  `);
})();

// Define API Endpoints

// Register a click
app.post('/click', async (request, reply) => {
  try {
    const id = uuidv4();
    const timestamp = new Date().toISOString();

    await db.run('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', [id, timestamp]);

    reply.code(201).send({ message: 'Click registered successfully' });
  } catch (error) {
    reply.code(400).send({ error: 'Invalid request' });
  }
});

// Retrieve clicks
app.get('/clicks', async (request, reply) => {
  try {
    const { date, direction } = request.query;

    if (!date || !direction || !['<', '>', '<=', '>='].includes(direction)) {
      return reply.code(400).send({ error: 'Invalid request' });
    }

    const rows = await db.all(`SELECT * FROM clicks WHERE timestamp ${direction} ?`, [date]);

    if (rows.length === 0) {
      return reply.code(404).send({ error: 'No clicks found' });
    }

    reply.code(200).send(rows);
  } catch (error) {
    reply.code(400).send({ error: 'Invalid request' });
  }
});

// Start the server
const start = async () => {
  try {
    await app.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server is running on http://0.0.0.0:5000');
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

start();