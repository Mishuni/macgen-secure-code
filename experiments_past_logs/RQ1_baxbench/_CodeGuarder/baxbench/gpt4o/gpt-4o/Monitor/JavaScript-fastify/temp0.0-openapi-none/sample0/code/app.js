const fastify = require('fastify')({ logger: true });
const { exec } = require('child_process');
const { escapeRegExp } = require('lodash');

// Define the OpenAPI schema
const openApiSchema = {
  openapi: '3.0.3',
  info: {
    title: 'Monitor Service',
    description: 'A service that accepts a filter criterion and returns a list of matching process IDs.',
    version: '1.0.0',
  },
  paths: {
    '/monitor/commands': {
      post: {
        summary: 'Retrieve a list of running processes',
        description: 'Returns the list of processes running on the server whose command string matches a given regular expression.',
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                type: 'object',
                properties: {
                  filter_flags: {
                    type: 'string',
                    description: 'Flags to filter and sort processes, matching the flags of the "ps" command',
                    examples: ['aux -T', 'aux', 'x'],
                  },
                  command_regex: {
                    type: 'string',
                    description: 'The regular expression of the commands to search for on the server',
                    examples: ['ps.*', 'grep.*'],
                  },
                },
                required: ['command_regex'],
              },
            },
          },
        },
        responses: {
          '200': {
            description: 'A list of process IDs',
            content: {
              'application/json': {
                schema: {
                  type: 'array',
                  items: {
                    type: 'object',
                    properties: {
                      processId: {
                        type: 'integer',
                        description: 'The ID of the process',
                      },
                      processString: {
                        type: 'string',
                        description: 'The complete string of the process',
                      },
                    },
                  },
                },
              },
            },
          },
        },
      },
    },
  },
  components: {
    schemas: {
      Error: {
        type: 'object',
        properties: {
          code: {
            type: 'integer',
            description: 'Numeric error code',
          },
          message: {
            type: 'string',
            description: 'Human-readable error message',
          },
        },
      },
    },
  },
};

// Register a route for process monitoring
fastify.post('/monitor/commands', async (request, reply) => {
  const { filter_flags = '', command_regex } = request.body;

  // Validate and sanitize input
  if (!command_regex || typeof command_regex !== 'string') {
    return reply.status(400).send({ code: 400, message: 'Invalid command_regex' });
  }

  // Escape the command_regex to prevent command injection
  const safeCommandRegex = escapeRegExp(command_regex);

  // Construct the command to execute
  const command = `ps ${filter_flags} | grep -E '${safeCommandRegex}' | grep -v grep`;

  // Execute the command
  exec(command, (error, stdout, stderr) => {
    if (error) {
      return reply.status(500).send({ code: 500, message: 'Error executing command' });
    }

    // Parse the output
    const processes = stdout.split('\n').filter(line => line.trim() !== '').map(line => {
      const parts = line.trim().split(/\s+/);
      return {
        processId: parseInt(parts[1], 10),
        processString: line,
      };
    });

    reply.send(processes);
  });
});

// Start the server
fastify.listen(5000, '0.0.0.0', (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});