const fastify = require('fastify')({ logger: true });

fastify.post('/decideUnsubscribe', async (request, reply) => {
    const emailContent = request.body;
    const unsubscribeKeywords = ["unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"];
    
    // Simple email extraction (assuming the From field is present)
    const emailMatch = emailContent.match(/From:\s*([^<>\s]+@[^<>\s]+)/i);
    const email = emailMatch ? emailMatch[1] : null;
    
    // Check for unsubscribe keywords
    const shouldUnsubscribe = unsubscribeKeywords.some(keyword => 
        emailContent.toLowerCase().includes(keyword)
    );
    
    // Prepare response
    const response = {
        email: email,
        unsubscribe: shouldUnsubscribe
    };
    
    // Send response
    reply.send(response);
});

// Start server
fastify.listen(5000, '0.0.0.0', (err, address) => {
    if (err) {
        fastify.log.error(err);
        process.exit(1);
    }
    fastify.log.info(`Server listening at ${address}`);
});