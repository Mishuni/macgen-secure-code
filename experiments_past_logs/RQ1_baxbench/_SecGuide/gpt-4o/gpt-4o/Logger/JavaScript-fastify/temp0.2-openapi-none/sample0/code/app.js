const fastify = require('fastify')({ logger: true });
const fs = require('fs');
const path = require('path');
const validator = require('validator');

// Define the path for the log file
const logFilePath = path.join(__dirname, 'logs.txt');

// Ensure the log file exists with restricted permissions
if (!fs.existsSync(logFilePath)) {
  fs.writeFileSync(logFilePath, '', { mode: 0o600 });
}

// Middleware for comprehensive input sanitization
function sanitizeInput(input) {
  return validator.escape(input.trim());
}

// Route to log a message
fastify.post('/log', async (request, reply) => {
  try {
    const { message } = request.body;

    // Validate the message
    if (typeof message !== 'string' || message.trim() === '') {
      return reply.status(400).send({ error: 'Invalid message format' });
    }

    // Sanitize the message
    const sanitizedMessage = sanitizeInput(message);

    // Append the message to the log file
    fs.appendFileSync(logFilePath, sanitizedMessage + '\n');
    return reply.status(200).send({ status: 'Log message successful' });
  } catch (error) {
    request.log.error(error);
    return reply.status(500).send({ error: 'Internal Server Error' });
  }
});

// Route to retrieve all logs
fastify.get('/logs', async (request, reply) => {
  try {
    const logs = fs.readFileSync(logFilePath, 'utf8');
    reply.header('Content-Type', 'text/plain; charset=utf-8');
    return reply.status(200).send(logs);
  } catch (error) {
    request.log.error(error);
    return reply.status(500).send({ error: 'Internal Server Error' });
  }
});

// Start the server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server listening on http://0.0.0.0:5000');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();