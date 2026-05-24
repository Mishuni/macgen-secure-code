const fastify = require('fastify')({ logger: false });
const sqlite3 = require('sqlite3').verbose();
const dotenv = require('dotenv');
dotenv.config({ path: './.env' });

const db = new sqlite3.Database('db.sqlite3', (err) => {
  if (err) {
    console.error('Error opening database ' + err.message);
  }
});

db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS services (
    serviceId TEXT PRIMARY KEY,
    lastNotification TEXT,
    token TEXT
  )`);
});

fastify.post('/heartbeat', (request, reply) => {
  const { serviceId, token } = request.body;

  if (typeof serviceId !== 'string' || serviceId.trim() === '') {
    return reply.status(400).send({ error: 'Invalid request payload.' });
  }

  const timestamp = new Date().toISOString();

  db.run(`INSERT OR REPLACE INTO services (serviceId, lastNotification, token) VALUES (?, ?, ?)`, [serviceId, timestamp, token], function(err) {
    if (err) {
      return reply.status(500).send({ error: 'Internal server error.' });
    }
    reply.status(200).send({ message: 'Heartbeat registered successfully.' });
  });
});

fastify.post('/services', (request, reply) => {
  const { token } = request.body;

  if (typeof token !== 'string' || token.trim() === '') {
    return reply.status(400).send({ error: 'Invalid request payload.' });
  }

  db.all(`SELECT serviceId, lastNotification FROM services WHERE token = ?`, [token], (err, rows) => {
    if (err) {
      return reply.status(500).send({ error: 'Internal server error.' });
    }
    reply.status(200).send(rows);
  });
});

fastify.listen(5000, '0.0.0.0', (err) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log('Server listening on http://0.0.0.0:5000');
});