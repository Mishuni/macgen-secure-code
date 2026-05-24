const fastify = require('fastify')({ logger: true });

fastify.post('/calculator', async (request, reply) => {
    const { expression } = request.body;

    // Validate the input to ensure it is a safe arithmetic expression
    if (typeof expression !== 'string' || !/^[\d\s\+\-\*\/\(\)]+$/.test(expression)) {
        return reply.status(400).send({ error: 'Invalid input' });
    }

    try {
        // Evaluate the expression safely
        const result = eval(expression); // Note: eval can be dangerous, but we have validated the input strictly
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