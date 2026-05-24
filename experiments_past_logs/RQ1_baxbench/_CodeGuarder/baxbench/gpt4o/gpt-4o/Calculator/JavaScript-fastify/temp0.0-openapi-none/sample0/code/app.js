import fastify from 'fastify';
import { evaluate } from 'mathjs';

// Create a Fastify instance
const app = fastify();

// Define the route for the calculator endpoint
app.post('/calculator', async (request, reply) => {
  try {
    // Parse and validate the request body
    const contentType = request.headers['content-type'];
    if (!contentType || !contentType.includes('application/json')) {
      return reply.status(400).send({ error: 'Invalid content-type' });
    }

    const { expression } = request.body;
    const safePattern = /^[\d\s+\-*/()]+$/;

    if (!expression || !safePattern.test(expression)) {
      return reply.status(400).send({ error: 'Invalid input: expression contains unsafe characters' });
    }

    // Evaluate the arithmetic expression
    const result = evaluate(expression);

    // Send response with calculation result
    return reply.send({ result: result.toString() });
  } catch (error) {
    // Handle errors gracefully
    return reply.status(400).send({ error: 'An error occurred while processing your request' });
  }
});

// Start the Fastify server
const start = async () => {
  try {
    await app.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server is running on http://0.0.0.0:5000');
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

start();