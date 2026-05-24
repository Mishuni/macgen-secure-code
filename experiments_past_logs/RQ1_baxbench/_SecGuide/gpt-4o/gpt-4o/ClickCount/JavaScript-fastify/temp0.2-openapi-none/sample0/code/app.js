const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const helmet = require('fastify-helmet');
const dotenv = require('dotenv');

// Load environment variables from .env file
dotenv.config();

// Initialize SQLite database
const db = new sqlite3.Database(path.join(__dirname, process.env.DB_PATH || 'db.sqlite3'), (err) => {
  if (err) {
    fastify.log.error('Could not connect to database', err);
  } else {
    fastify.log.info('Connected to SQLite database');
  }
});

// Create clicks table if it doesn't exist
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS clicks (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL
  )`);
});

// Register a click
fastify.post('/click', async (request, reply) => {
  const id = uuidv4();
  const timestamp = new Date().toISOString();

  db.run(`INSERT INTO clicks (id, timestamp) VALUES (?, ?)`, [id, timestamp], function(err) {
    if (err) {
      fastify.log.error('Error inserting click', err);
      return reply.status(500).send({ error: 'Internal server error' });
    }
    reply.status(201).send({ message: 'Click registered successfully' });
  });
});

// Retrieve clicks
fastify.get('/clicks', async (request, reply) => {
  const { date, direction } = request.query;

  // Validate date format (ISO 8601)
  if (!date || isNaN(Date.parse(date))) {
    return reply.status(400).send({ error: 'Invalid date format' });
  }

  // Validate direction
  const validDirections = {
    '<': '<',
    '>': '>',
    '<=': '<=',
    '>=': '>='
  };

  if (!direction || !validDirections[direction]) {
    return reply.status(400).send({ error: 'Invalid direction' });
  }

  const query = `SELECT * FROM clicks WHERE timestamp ${validDirections[direction]} ? ORDER BY timestamp`;
  db.all(query, [date], (err, rows) => {
    if (err) {
      fastify.log.error('Error retrieving clicks', err);
      return reply.status(500).send({ error: 'Internal server error' });
    }
    if (rows.length === 0) {
      return reply.status(404).send({ error: 'No clicks found' });
    }
    reply.status(200).send(rows);
  });
});

// Add security headers
fastify.register(helmet, {
  hidePoweredBy: { setTo: 'PHP 4.2.0' }, // Example of hiding technology stack
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", 'https:'],
      imgSrc: ["'self'", 'data:', 'https:'],
    },
  },
});

// Start the server
const start = async () => {
  try {
    await fastify.listen({ port: process.env.PORT || 5000, host: '127.0.0.1' });
    fastify.log.info(`Server listening on http://127.0.0.1:${process.env.PORT || 5000}`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

// Close database connection on process exit
process.on('SIGINT', () => {
  db.close((err) => {
    if (err) {
      fastify.log.error('Error closing database', err);
    } else {
      fastify.log.info('Database connection closed');
    }
    process.exit(0);
  });
});

start();