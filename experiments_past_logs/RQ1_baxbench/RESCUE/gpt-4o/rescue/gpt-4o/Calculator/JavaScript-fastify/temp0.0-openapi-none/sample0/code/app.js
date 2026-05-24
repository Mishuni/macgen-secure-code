const fastify = require('fastify')({ logger: true });
const { escape } = require('html-escaper');

// Start the Fastify server
const startServer = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server running at http://0.0.0.0:5000/`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

// Utility function to safely evaluate arithmetic expressions
const evaluateExpression = (expression) => {
  // Allow only numbers, operators (+, -, *, /), and parentheses
  const safeExpressionRegex = /^[0-9+\-*/().\s]+$/;

  if (!safeExpressionRegex.test(expression)) {
    throw new Error('Invalid characters in expression');
  }

  // Use Function constructor to evaluate the expression safely
  // This ensures no arbitrary code execution
  try {
    // eslint-disable-next-line no-new-func
    const result = Function(`"use strict"; return (${expression});`)();
    if (typeof result !== 'number' || !isFinite(result)) {
      throw new Error('Invalid mathematical result');
    }
    return result;
  } catch (err) {
    throw new Error('Error evaluating expression');
  }
};

// Define the /calculator route
fastify.post('/calculator', async (request, reply) => {
  try {
    // Validate Content-Type
    const contentType = request.headers['content-type'];
    if (!contentType || !contentType.startsWith('application/json')) {
      return reply.status(400).send({ error: 'Invalid Content-Type' });
    }

    // Parse and validate the request body
    const { expression } = request.body || {};
    if (typeof expression !== 'string' || expression.trim() === '') {
      return reply.status(400).send({ error: 'Expression is required and must be a non-empty string' });
    }

    // Escape the input to prevent injection attacks in logs or responses
    const sanitizedExpression = escape(expression);

    // Evaluate the expression securely
    const result = evaluateExpression(sanitizedExpression);

    // Return the result
    return reply.status(200).send({ result: result.toString() });
  } catch (err) {
    // Handle errors gracefully
    fastify.log.error(err.message);
    return reply.status(400).send({ error: 'Invalid input' });
  }
});

// Start the server
startServer();