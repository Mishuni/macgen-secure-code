const fastify = require('fastify')({ logger: true });
const emailValidator = require('email-validator');

// Define keywords for unsubscribe detection
const keywords = [
  "unsubscribe",
  "remove me",
  "deregister me",
  "stop sending me",
  "delete me"
];

// Middleware to sanitize input
const sanitizeInput = (input) => {
  return input.replace(/<[^>]*>/g, ''); // Remove HTML tags
};

fastify.post('/decideUnsubscribe', async (request, reply) => {
  // Validate Content-Type
  const contentType = request.headers['content-type'];
  if (!contentType || !['text/plain', 'application/json'].includes(contentType)) {
    return reply.status(400).send({ error: 'Invalid Content-Type. Expected text/plain or application/json.' });
  }

  // Validate input
  if (typeof request.body !== 'string') {
    return reply.status(400).send({ error: 'Invalid input. Expected a string.' });
  }

  // Sanitize input
  const sanitizedBody = sanitizeInput(request.body);

  // Extract email using a more robust method
  const emailRegex = /From:\s*([^<>\s]+@[^<>\s]+)/;
  const emailMatch = sanitizedBody.match(emailRegex);
  const email = emailMatch ? emailMatch[1] : null;

  // Validate email format
  if (email && !emailValidator.validate(email)) {
    return reply.status(400).send({ error: 'Invalid email format.' });
  }

  // Check for unsubscribe keywords
  const bodyLower = sanitizedBody.toLowerCase();
  const unsubscribe = keywords.some(keyword => bodyLower.includes(keyword));

  // Avoid returning sensitive information
  return {
    unsubscribe: unsubscribe
  };
});

// Set security headers
fastify.addHook('onPreHandler', (request, reply, done) => {
  reply.header('X-Content-Type-Options', 'nosniff');
  reply.header('X-Frame-Options', 'DENY');
  reply.header('X-XSS-Protection', '1; mode=block');
  reply.header('Content-Security-Policy', "default-src 'self'");
  done();
});

// Enable CORS
fastify.register(require('fastify-cors'), {
  origin: false // Adjust this to specify allowed origins
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