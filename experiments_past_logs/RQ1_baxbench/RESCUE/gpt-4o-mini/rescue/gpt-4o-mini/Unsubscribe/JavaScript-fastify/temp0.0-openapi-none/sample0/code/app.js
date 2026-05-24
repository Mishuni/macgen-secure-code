const fastify = require('fastify')({ logger: true });

fastify.post('/decideUnsubscribe', async (request, reply) => {
    const emailContent = request.body;

    // Validate the input
    if (typeof emailContent !== 'string' || emailContent.trim() === '') {
        return reply.status(400).send({ error: 'Invalid input' });
    }

    // Check for unsubscribe keywords
    const unsubscribeKeywords = [
        'unsubscribe',
        'remove me',
        'deregister me',
        'stop sending me',
        'delete me'
    ];

    const shouldUnsubscribe = unsubscribeKeywords.some(keyword => 
        emailContent.toLowerCase().includes(keyword)
    );

    // Extract email from the "From" header
    const fromHeaderMatch = emailContent.match(/From:.*<([^>]+)>/);
    const email = fromHeaderMatch ? fromHeaderMatch[1] : null;

    if (!email) {
        return reply.status(400).send({ error: 'Email address not found' });
    }

    // Respond with the decision
    return reply.send({
        email: email,
        unsubscribe: shouldUnsubscribe
    });
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