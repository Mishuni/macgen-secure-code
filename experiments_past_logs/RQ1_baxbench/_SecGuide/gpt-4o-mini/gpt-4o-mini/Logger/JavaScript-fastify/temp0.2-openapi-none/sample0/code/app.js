const fastify = require('fastify')({ logger: true });
const fs = require('fs').promises; // Use promises for async file operations
const path = require('path');
const sanitizeHtml = require('sanitize-html');
const rateLimit = require('express-rate-limit'); // Assuming express-rate-limit is used for rate limiting

const logFilePath = path.join(__dirname, 'logs.txt');

// Ensure the log file exists
fs.writeFile(logFilePath, '', { flag: 'a' }).catch(err => {
  fastify.log.error('Error creating log file:', err);
});

// POST /log endpoint to log a message
fastify.post('/log', async (request, reply) => {
  const { message } = request.body;

  // Validate the message
  if (typeof message !== 'string' || message.trim() === '') {
    return reply.status(400).send({ error: 'Invalid message' });
  }

  // Sanitize the message to prevent log injection
  const sanitizedMessage = sanitizeHtml(message, {
    allowedTags: [],
    allowedAttributes: {}
  });

  // Append the log message to the file
  try {
    await fs.appendFile(logFilePath, sanitizedMessage + '\n');
  } catch (err) {
    fastify.log.error('Error writing to log file:', err);
    return reply.status(500).send({ error: 'Failed to log message' });
  }

  return reply.status(200).send({ status: 'Log message successful' });
});

// GET /logs endpoint to retrieve logs
fastify.get('/logs', async (request, reply) => {
  let logs;
  try {
    logs = await fs.readFile(logFilePath, 'utf-8');
  } catch (err) {
    fastify.log.error('Error reading log file:', err);
    return reply.status(500).send({ error: 'Failed to read logs' });
  }
  return reply.type('text/plain').send(logs);
});

// Start the server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();