const fastify = require('fastify')({ logger: true });
const { Parser } = require('expr-eval');

// Function to validate the expression
const isValidExpression = (expression) => {
  // Check for valid characters and prevent overly complex expressions
  const regex = /^[\d\s\+\-\*\/\(\)]+$/;
  const maxLength = 100; // Limit the length of the expression
  return regex.test(expression) && expression.length <= maxLength;
};

fastify.post('/calculator', async (request, reply) => {
  const { expression } = request.body;

  // Validate the input
  if (typeof expression !== 'string' || !isValidExpression(expression)) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  try {
    // Evaluate the expression safely using expr-eval
    const result = Parser.evaluate(expression);
    
    // Check for division by zero or other arithmetic errors
    if (result === Infinity || result === -Infinity) {
      return reply.status(400).send({ error: 'Arithmetic error' });
    }

    return { result: result.toString() };
  } catch (error) {
    return reply.status(400).send({ error: 'Invalid input' });
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