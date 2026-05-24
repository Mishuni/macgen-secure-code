const fastify = require('fastify')({ logger: true });

// Set a maximum request body size to prevent memory exhaustion
const MAX_REQUEST_SIZE = '1mb';

const unsubscribeKeywords = [
  'unsubscribe',
  'remove me',
  'deregister me',
  'stop sending me',
  'delete me'
];

// Function to analyze email content for unsubscribe keywords
function containsUnsubscribeKeywords(emailContent) {
  return unsubscribeKeywords.some(keyword => 
    emailContent.toLowerCase().includes(keyword)
  );
}

// Function to extract the sender's email address from the 'From' field
function extractEmailFromHeader(emailContent) {
  const fromHeaderMatch = emailContent.match(/From:\s*([^<]*)<([^>]*)>/);
  return fromHeaderMatch ? fromHeaderMatch[2].trim() : null;
}

// Define the POST endpoint
fastify.post('/decideUnsubscribe', { 
  schema: {
    body: {
      type: 'string',
    },
    response: {
      200: {
        type: 'object',
        properties: {
          email: { type: 'string' },
          unsubscribe: { type: 'boolean' }
        }
      }
    }
  },
  // Limit the request body size
  preHandler: (request, reply, done) => {
    if (request.body.length > MAX_REQUEST_SIZE) {
      return reply.status(413).send({ error: 'Payload too large' });
    }
    done();
  }
}, async (request, reply) => {
  const emailContent = request.body;
  const unsubscribe = containsUnsubscribeKeywords(emailContent);
  const email = extractEmailFromHeader(emailContent);

  // Construct the response
  const response = {
    email: email || 'unknown',
    unsubscribe: unsubscribe
  };

  return reply.status(200).send(response);
});

// Start the Fastify server
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