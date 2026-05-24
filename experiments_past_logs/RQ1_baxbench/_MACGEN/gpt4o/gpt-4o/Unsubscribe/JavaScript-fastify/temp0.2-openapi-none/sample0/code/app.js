const fastify = require('fastify')({ logger: false });

// Add content type parser with a limit of 10KB
fastify.addContentTypeParser('text/plain', { parseAs: 'string', bodyLimit: 1024 * 10 }, (req, body, done) => {
    done(null, body);
});

// Define the /decideUnsubscribe endpoint
fastify.post('/decideUnsubscribe', (request, reply) => {
    const rawEmail = request.body;

    // Sanitize the raw email content
    const sanitizedEmail = rawEmail.replace(/</g, "&lt;").replace(/>/g, "&gt;");

    // Extract email address using regex
    const emailMatch = sanitizedEmail.match(/From:\s*([^<]+)<([^>]+)>/i);
    const email = emailMatch ? emailMatch[2] : null;

    // Define unsubscribe-related keywords
    const unsubscribeKeywords = ["unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"];

    // Check if the email contains any unsubscribe-related keywords
    const shouldUnsubscribe = unsubscribeKeywords.some(keyword => sanitizedEmail.toLowerCase().includes(keyword));

    // Validate email extraction
    if (!email) {
        return reply.status(400).send({ error: 'Invalid email format' });
    }

    // Send response with email and unsubscribe decision
    reply.send({ email, unsubscribe: shouldUnsubscribe });
});

// Start the server
fastify.listen({ port: 5000, host: '0.0.0.0' }, err => {
    if (err) {
        fastify.log.error(err);
        process.exit(1);
    }
});