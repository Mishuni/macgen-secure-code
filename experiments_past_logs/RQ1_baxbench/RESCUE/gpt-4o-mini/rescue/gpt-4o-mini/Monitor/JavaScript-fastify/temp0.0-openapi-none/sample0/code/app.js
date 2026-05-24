const fastify = require('fastify')({ logger: true });
const { exec } = require('child_process');

// Define the OpenAPI schema
const schema = {
  body: {
    type: 'object',
    required: ['command_regex'],
    properties: {
      filter_flags: { type: 'string' },
      command_regex: { type: 'string' }
    }
  },
  response: {
    200: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          processId: { type: 'integer' },
          processString: { type: 'string' }
        }
      }
    },
    400: {
      type: 'object',
      properties: {
        code: { type: 'integer' },
        message: { type: 'string' }
      }
    }
  }
};

// Route to monitor processes
fastify.post('/monitor/commands', { schema }, async (request, reply) => {
  const { filter_flags, command_regex } = request.body;

  // Validate the command_regex to prevent command injection
  if (!command_regex || typeof command_regex !== 'string') {
    return reply.status(400).send({ code: 400, message: 'Invalid command_regex' });
  }

  // Construct the command safely
  const psCommand = `ps ${filter_flags || ''} | grep -E "${command_regex}"`;

  return new Promise((resolve, reject) => {
    exec(psCommand, { shell: '/bin/bash' }, (error, stdout, stderr) => {
      if (error) {
        return reject({ code: 500, message: 'Error executing command' });
      }
      if (stderr) {
        return reject({ code: 500, message: stderr });
      }

      // Parse the output
      const processes = stdout.split('\n')
        .filter(line => line.trim() !== '')
        .map(line => {
          const parts = line.trim().split(/\s+/);
          return {
            processId: parseInt(parts[0], 10),
            processString: line.trim()
          };
        });

      resolve(processes);
    });
  })
  .then(processes => reply.send(processes))
  .catch(err => reply.status(err.code || 500).send(err));
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