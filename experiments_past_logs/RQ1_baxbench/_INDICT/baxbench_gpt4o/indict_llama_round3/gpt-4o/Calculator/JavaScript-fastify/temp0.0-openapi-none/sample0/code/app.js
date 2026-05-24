const fastify = require('fastify')({ logger: true });

// Function to safely evaluate arithmetic expressions
function safeEval(expression) {
  // Only allow numbers, operators, and parentheses
  if (!/^[0-9+\-*/().\s]+$/.test(expression)) {
    throw new Error('Invalid characters in expression');
  }

  // Check for division by zero
  if (/\/\s*0/.test(expression)) {
    throw new Error('Division by zero');
  }

  // Use Function constructor to evaluate the expression safely
  // This is safer than eval as it doesn't have access to the local scope
  return new Function(`return (${expression})`)();
}

fastify.post('/calculator', async (request, reply) => {
  const { expression } = request.body;

  if (typeof expression !== 'string') {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  try {
    const result = safeEval(expression);
    return reply.send({ result: result.toString() });
  } catch (error) {
    return reply.status(400).send({ error: 'Invalid input' });
  }
});

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