const fastify = require('fastify')({ logger: true });
const fs = require('fs').promises;
const path = require('path');

// Change log file path to a more secure and predictable location
const logFilePath = path.resolve(__dirname, 'logs.txt'); // Using application directory for logs

// POST /log endpoint to log a message
fastify.post('/log', async (request, reply) => {
  const { message } = request.body;

  if (!message || typeof message !== 'string') {
    return reply.status(400).send({ error: 'Invalid message' });
  }

  // Sanitize log message
  const sanitizedMessage = message.replace(/[\r\n]+/g, ' ');
  // Limit log message size
  const limitedMessage = sanitizedMessage.length > 256 ? sanitizedMessage.substring(0, 256) : sanitizedMessage;

  try {
    await fs.appendFile(logFilePath, limitedMessage + '\n');
    return reply.status(200).send({ status: 'Log message successful' });
  } catch (error) {
    request.log.error(error);
    return reply.status(500).send({ error: 'Failed to log message' });
  }
});

// GET /logs endpoint to retrieve all logged messages
fastify.get('/logs', async (request, reply) => {
  try {
    const logs = await fs.readFile(logFilePath, 'utf-8');
    return reply.type('text/plain').send(logs);
  } catch (error) {
    request.log.error(error);
    return reply.status(500).send({ error: 'Failed to retrieve logs' });
  }
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