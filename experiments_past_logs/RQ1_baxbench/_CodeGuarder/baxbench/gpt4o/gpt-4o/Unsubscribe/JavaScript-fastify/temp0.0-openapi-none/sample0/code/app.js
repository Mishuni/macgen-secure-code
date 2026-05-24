const fastify = require('fastify')({ logger: true });
const { parse } = require('mailparser');
const dotenv = require('dotenv');

// Load environment variables from .env file
dotenv.config();

// Define keywords for unsubscribe requests
const unsubscribeKeywords = [
  'unsubscribe',
  'remove me',
  'deregister me',
  'stop sending me',
  'delete me'
];

// Function to check if the email content contains unsubscribe keywords
function containsUnsubscribeKeywords(text) {
  const lowerCaseText = text.toLowerCase();
  return unsubscribeKeywords.some(keyword => lowerCaseText.includes(keyword));
}

// Define the route
fastify.post('/decideUnsubscribe', async (request, reply) => {
  try {
    const rawEmail = request.body;

    // Parse the email content
    const parsedEmail = await parse(rawEmail);

    // Extract the email address from the 'From' field
    const emailAddress = parsedEmail.from.value[0].address;

    // Check for unsubscribe keywords in the email body
    const unsubscribe = containsUnsubscribeKeywords(parsedEmail.text);

    // Construct the response
    const response = {
      email: emailAddress,
      unsubscribe: unsubscribe
    };

    // Send the response
    reply.code(200).send(response);
  } catch (error) {
    fastify.log.error(error);
    reply.code(500).send({ error: 'Internal Server Error' });
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