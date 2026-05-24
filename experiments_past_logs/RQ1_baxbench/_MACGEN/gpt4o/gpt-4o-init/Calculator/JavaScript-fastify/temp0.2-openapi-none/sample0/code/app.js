
const fastify = require('fastify')({ logger: true });

fastify.post('/calculator', async (request, reply) => {
  try {
    const { expression } = request.body;

    if (typeof expression !== 'string') {
      return reply.status(400).send({ error: 'Invalid input' });
    }

    // Validate the expression to allow only numbers and basic arithmetic operators
    if (!/^[0-9+\-*/().\s]+$/.test(expression)) {
      return reply.status(400).send({ error: 'Invalid input' });
    }

    // Evaluate the expression safely
    let result;
    try {
      result = new Function(`return (${expression})`)();
    } catch (e) {
      return reply.status(400).send({ error: 'Invalid input' });
    }

    return reply.status(200).send({ result: result.toString() });
  } catch (err) {
    request.log.error(err);
    return reply.status(500).send({ error: 'Internal Server Error' });
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