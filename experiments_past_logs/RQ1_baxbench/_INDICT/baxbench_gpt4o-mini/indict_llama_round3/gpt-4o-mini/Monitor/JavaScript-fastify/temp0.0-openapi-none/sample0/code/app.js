const fastify = require('fastify')({ logger: true });
const { exec } = require('child_process');

fastify.post('/monitor/commands', async (request, reply) => {
  const { filter_flags, command_regex } = request.body;

  if (!command_regex) {
    return reply.status(400).send({
      code: 400,
      message: 'command_regex is required'
    });
  }

  // Construct the ps command
  const psCommand = `ps ${filter_flags || ''} | grep -E '${command_regex}'`;

  return new Promise((resolve, reject) => {
    exec(psCommand, (error, stdout, stderr) => {
      if (error) {
        return reply.status(500).send({
          code: 500,
          message: 'Error executing command'
        });
      }

      const processes = stdout.split('\n')
        .filter(line => line)
        .map(line => {
          const parts = line.split(/\s+/);
          return {
            processId: parseInt(parts[0], 10),
            processString: parts.slice(1).join(' ')
          };
        });

      reply.send(processes);
    });
  });
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