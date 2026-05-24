const fastify = require('fastify')({ logger: true });

fastify.post('/calculator', async (request, reply) => {
  const { expression } = request.body;

  if (typeof expression !== 'string') {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  try {
    const result = evaluateExpression(expression);
    return { result: result.toString() };
  } catch (error) {
    return reply.status(400).send({ error: 'Invalid input' });
  }
});

// A simple and safe evaluation function for arithmetic expressions
function evaluateExpression(expr) {
  // Allow only numbers, operators, and whitespace
  if (/^[0-9+\-*/().\s]+$/.test(expr)) {
    // Use a simple parser to evaluate the expression
    return new Function(`'use strict'; return (${expr})`)();
  } else {
    throw new Error('Invalid expression');
  }
}

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