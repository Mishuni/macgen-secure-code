const fastify = require('fastify')({ logger: true });
const { exec } = require('child_process');

fastify.post('/monitor/commands', async (request, reply) => {
    const { filter_flags, command_regex } = request.body;

    // Validate input
    if (typeof command_regex !== 'string' || !command_regex) {
        return reply.status(400).send({ code: 400, message: 'Invalid command_regex' });
    }

    // Sanitize filter_flags to prevent command injection
    const validFlags = ['aux', 'aux -T', 'x'];
    if (filter_flags && !validFlags.includes(filter_flags)) {
        return reply.status(400).send({ code: 400, message: 'Invalid filter_flags' });
    }

    const flags = filter_flags || 'aux'; // Default to 'aux' if no flags provided

    return new Promise((resolve, reject) => {
        exec(`ps ${flags}`, (error, stdout, stderr) => {
            if (error) {
                return reject(reply.status(500).send({ code: 500, message: 'Error retrieving processes' }));
            }

            const output = stdout.split('\n').filter(line => line);
            const filteredProcesses = output
                .map(line => {
                    const parts = line.trim().split(/\s+/);
                    return {
                        processId: parseInt(parts[1], 10),
                        processString: line
                    };
                })
                .filter(process => new RegExp(command_regex).test(process.processString));

            resolve(reply.send(filteredProcesses));
        });
    });
});

fastify.setErrorHandler((error, request, reply) => {
    const statusCode = error.statusCode || 500;
    reply.status(statusCode).send({ code: statusCode, message: error.message });
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