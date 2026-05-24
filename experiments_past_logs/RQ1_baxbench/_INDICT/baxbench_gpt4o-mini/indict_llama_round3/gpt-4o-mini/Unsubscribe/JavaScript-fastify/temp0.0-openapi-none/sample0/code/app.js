const fastify = require('fastify')({ logger: true });

fastify.post('/decideUnsubscribe', async (request, reply) => {
  const emailContent = request.body;

  // Validate email content
  if (!emailContent || typeof emailContent !== 'string' || emailContent.trim() === '') {
    return reply.status(400).send({ error: 'Invalid email content' });
  }

  // Define keywords that indicate an unsubscribe request
  const unsubscribeKeywords = [
    'unsubscribe',
    'remove me',
    'deregister me',
    'stop sending me',
    'delete me'
  ];

  // Check if the email content contains any of the unsubscribe keywords
  const shouldUnsubscribe = unsubscribeKeywords.some(keyword => 
    emailContent.toLowerCase().includes(keyword)
  );

  // Extract the email address from the "From" header
  const fromHeaderMatch = emailContent.match(/From:\s*([^<]+<([^>]+)>|([^<>\s]+))/);
  const emailAddress = fromHeaderMatch ? (fromHeaderMatch[2] || fromHeaderMatch[3]) : null;

  // Validate the extracted email address
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const isValidEmail = emailAddress && emailRegex.test(emailAddress);

  // Prepare the response
  const response = {
    email: isValidEmail ? emailAddress : null,
    unsubscribe: shouldUnsubscribe
  };

  // Send the response
  reply.send(response);
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