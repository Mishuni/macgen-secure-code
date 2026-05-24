const fastify = require('fastify')({ logger: true });
const { v4: uuidv4 } = require('uuid');
const cookie = require('@fastify/cookie');
const dotenv = require('dotenv');
const emailParser = require('email-addresses');

// Load environment variables from .env file
dotenv.config();

fastify.register(cookie, {
  secret: process.env.COOKIE_SECRET, // Use environment variable for cookie secret
  parseOptions: {} // options for parsing cookies
});

const unsubscribeKeywords = [
  "unsubscribe",
  "remove me",
  "deregister me",
  "stop sending me",
  "delete me"
];

// Middleware to generate CSRF token on form rendering
fastify.addHook('preHandler', async (request, reply) => {
  if (request.method === 'GET' || request.method === 'POST') {
    const csrfToken = uuidv4();
    reply.setCookie('csrfToken', csrfToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production', // Set secure only in production
      sameSite: 'Strict'
    });
    request.csrfToken = csrfToken; // Store CSRF token in request for server-side validation
  }
});

fastify.post('/decideUnsubscribe', async (request, reply) => {
  // Set content type
  reply.header('Content-Type', 'application/json; charset=utf-8');

  // Validate CSRF token
  const formCsrfToken = request.body.csrfToken;
  const cookieCsrfToken = request.cookies.csrfToken;
  if (!formCsrfToken || formCsrfToken !== cookieCsrfToken || formCsrfToken !== request.csrfToken) {
    return reply.status(400).send({ error: 'Invalid CSRF token' });
  }

  // Extract email content
  const emailContent = request.body.emailContent;
  if (!emailContent || typeof emailContent !== 'string' || emailContent.length > 10000) {
    return reply.status(400).send({ error: 'Invalid email content' });
  }

  // Extract email address from the "From" header using a robust library
  const parsedEmail = emailParser.parseOneAddress(emailContent);
  const email = parsedEmail ? parsedEmail.address : null;

  if (!email) {
    return reply.status(400).send({ error: 'Email address not found' });
  }

  // Check for unsubscribe keywords
  const unsubscribe = unsubscribeKeywords.some(keyword =>
    emailContent.toLowerCase().includes(keyword)
  );

  // Respond with the decision
  return reply.send({
    email,
    unsubscribe
  });
});

// Start the server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' }); // Bind to all interfaces
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();