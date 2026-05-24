const fastify = require('fastify')({ logger: true });
const fs = require('fs');
const path = require('path');

// Define the log file path
const logFilePath = path.join(__dirname, 'logs.txt');

// Ensure the log file exists
fs.writeFileSync(logFilePath, '', { flag: 'a' }); // Create the file if it doesn't exist

// POST endpoint to log a message
fastify.post('/log', async (request, reply) => {
    const { message } = request.body;

    // Validate the input
    if (typeof message !== 'string' || message.trim() === '') {
        return reply.status(400).send({ error: 'Invalid message' });
    }

    // Sanitize the message to prevent injection attacks
    const sanitizedMessage = message.replace(/[\r\n]+/g, ' ').replace(/</g, '&lt;').replace(/>/g, '&gt;');

    // Log the message to the file
    fs.appendFileSync(logFilePath, `${sanitizedMessage}\n`, 'utf8');

    return reply.status(200).send({ status: 'Log message successful' });
});

// GET endpoint to retrieve logs
fastify.get('/logs', async (request, reply) => {
    try {
        const logs = fs.readFileSync(logFilePath, 'utf8');
        return reply.type('text/plain').send(logs);
    } catch (error) {
        request.log.error(error);
        return reply.status(500).send({ error: 'Unable to retrieve logs' });
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