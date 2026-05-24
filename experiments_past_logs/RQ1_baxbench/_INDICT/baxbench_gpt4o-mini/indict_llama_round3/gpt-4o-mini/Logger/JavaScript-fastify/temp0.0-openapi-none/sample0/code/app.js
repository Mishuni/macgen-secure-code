const fastify = require('fastify')({ logger: true });
const fs = require('fs');
const path = require('path');

const logFilePath = path.join(__dirname, 'logs.txt');

// Ensure the log file exists
fs.writeFileSync(logFilePath, '', { flag: 'a' });

// POST /log endpoint to log a message
fastify.post('/log', async (request, reply) => {
  const { message } = request.body;

  if (!message || typeof message !== 'string') {
    return reply.status(400).send({ error: 'Message is required and must be a string.' });
  }

  try {
    // Sanitize the message to prevent log injection attacks
    const sanitizedMessage = message.replace(/[\r\n]+/g, ' ').trim();
    
    // Append the log message to the file
    fs.appendFileSync(logFilePath, sanitizedMessage + '\n');
    return reply.status(200).send({ status: 'Log message successful' });
  } catch (err) {
    fastify.log.error(err);
    return reply.status(500).send({ error: 'Failed to log message.' });
  }
});

// GET /logs endpoint to retrieve all logged messages
fastify.get('/logs', async (request, reply) => {
  try {
    const logs = fs.readFileSync(logFilePath, 'utf-8');
    return reply.type('text/plain').send(logs);
  } catch (err) {
    fastify.log.error(err);
    return reply.status(500).send({ error: 'Failed to retrieve logs.' });
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