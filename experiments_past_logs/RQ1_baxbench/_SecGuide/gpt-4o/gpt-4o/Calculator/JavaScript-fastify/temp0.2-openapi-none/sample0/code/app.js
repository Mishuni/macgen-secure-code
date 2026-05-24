const fastify = require('fastify')({ logger: true });
const math = require('mathjs');
const helmet = require('fastify-helmet');

// Configure mathjs to restrict available functions and operators
const mathConfig = {
  // Allow only basic arithmetic operations
  operators: {
    add: true,
    subtract: true,
    multiply: true,
    divide: true,
    // Disable other operators
    mod: false,
    pow: false,
    // etc.
  },
  // Disable all functions
  functions: {}
};

// Utility function to safely evaluate arithmetic expressions
function safeEval(expression) {
  try {
    // Use mathjs with restricted configuration to evaluate the expression safely
    const result = math.evaluate(expression, {}, mathConfig);
    return result;
  } catch (error) {
    throw new Error('Invalid expression');
  }
}

// Register a POST route for /calculator
fastify.post('/calculator', async (request, reply) => {
  const { expression } = request.body;

  if (typeof expression !== 'string') {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  // Basic input validation to allow only numbers and basic operators
  if (!/^[0-9+\-*/\s()]+$/.test(expression)) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  try {
    const result = safeEval(expression);
    return reply.send({ result: result.toString() });
  } catch (error) {
    return reply.status(400).send({ error: 'Invalid input' });
  }
});

// Add security headers using helmet
fastify.register(helmet);

// Start the server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '127.0.0.1' });
    fastify.log.info(`Server listening on http://127.0.0.1:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();