const fastify = require('fastify')({ logger: true });
const fs = require('fs');
const path = require('path');

const LOG_FILE_PATH = path.join(__dirname, 'logs.txt');

// Ensure the log file exists with strict permissions
fs.open(LOG_FILE_PATH, 'a', 0o600, (err, fd) => {
  if (err) throw err;
  fs.close(fd, (err) => {
    if (err) throw err;
  });
});

// Route to log a message
fastify.post('/log', async (request, reply) => {
  const { message } = request.body;
  if (!message || typeof message !== 'string') {
    return reply.status(400).send({ error: 'Message is required and must be a string' });
  }

  // Sanitize the message to prevent injection attacks
  const sanitizedMessage = message.replace(/[\r\n]/g, ' ');

  // Use a write stream to handle concurrency better
  const logStream = fs.createWriteStream(LOG_FILE_PATH, { flags: 'a', mode: 0o600 });
  logStream.write(sanitizedMessage + '\n', (err) => {
    if (err) {
      fastify.log.error(err);
      return reply.status(500).send({ error: 'Failed to log message' });
    }
    reply.send({ status: 'Log message successful' });
  });
  logStream.end();
});

// Route to retrieve all logs
fastify.get('/logs', async (request, reply) => {
  fs.readFile(LOG_FILE_PATH, 'utf8', (err, data) => {
    if (err) {
      fastify.log.error(err);
      return reply.status(500).send({ error: 'Failed to retrieve logs' });
    }
    reply.type('text/plain').send(data);
  });
});

// Start the server
fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});