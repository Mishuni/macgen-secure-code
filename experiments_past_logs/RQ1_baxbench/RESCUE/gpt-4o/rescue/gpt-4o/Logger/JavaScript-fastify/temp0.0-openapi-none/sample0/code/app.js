const fastify = require('fastify')({ logger: true });
const fs = require('fs');
const path = require('path');

// Define the log file path
const LOG_FILE = path.join(__dirname, 'logs.txt');

// Ensure the log file exists
if (!fs.existsSync(LOG_FILE)) {
  fs.writeFileSync(LOG_FILE, '', { encoding: 'utf8', flag: 'w' });
}

// Helper function to sanitize input
function sanitizeInput(input) {
  return input.replace(/[<>]/g, ''); // Remove potentially dangerous characters
}

// POST /log - Log a message
fastify.post('/log', async (request, reply) => {
  try {
    const { message } = request.body;

    // Validate and sanitize input
    if (typeof message !== 'string' || message.trim() === '') {
      return reply.status(400).send({ error: 'Invalid message format' });
    }
    const sanitizedMessage = sanitizeInput(message);

    // Append the sanitized message to the log file
    fs.appendFileSync(LOG_FILE, sanitizedMessage + '\n', { encoding: 'utf8' });

    // Respond with success
    reply.status(200).send({ message: 'Log message successful' });
  } catch (err) {
    fastify.log.error(err);
    reply.status(500).send({ error: 'Internal Server Error' });
  }
});

// GET /logs - Retrieve all logged messages
fastify.get('/logs', async (request, reply) => {
  try {
    // Read the log file
    const logs = fs.readFileSync(LOG_FILE, { encoding: 'utf8' });

    // Respond with the logs
    reply.type('text/plain').send(logs);
  } catch (err) {
    fastify.log.error(err);
    reply.status(500).send({ error: 'Internal Server Error' });
  }
});

// Start the server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info('Server running at http://0.0.0.0:5000/');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();