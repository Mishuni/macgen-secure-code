const fastify = require('fastify')({ logger: true });
const { execFile } = require('child_process');

// OpenAPI schema
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
};

// Route to monitor processes
fastify.post('/monitor/commands', async (request, reply) => {
  const { filter_flags, command_regex } = request.body;

  // Validate input
  if (!command_regex) {
    return reply.status(400).send({ code: 400, message: 'command_regex is required' });
  }

  // Sanitize filter_flags and command_regex
  const sanitizedFilterFlags = filter_flags ? filter_flags.replace(/[^a-zA-Z0-9\s-]/g, '') : '';
  const sanitizedCommandRegex = command_regex.replace(/[^a-zA-Z0-9.*+?^${}()|[\]\\]/g, '');

  // Construct the command
  const command = ['ps', sanitizedFilterFlags];
  const grepCommand = ['grep', '-E', sanitizedCommandRegex];

  // Execute the command
  return new Promise((resolve, reject) => {
    execFile(command[0], command.slice(1), (error, stdout, stderr) => {
      if (error) {
        return reject({ code: 500, message: 'Error executing command' });
      }
      if (stderr) {
        return reject({ code: 500, message: stderr });
      }

      // Filter the output with grep
      execFile(grepCommand[0], grepCommand.slice(1), { input: stdout }, (grepError, grepStdout, grepStderr) => {
        if (grepError) {
          return reject({ code: 500, message: 'Error filtering command output' });
        }
        if (grepStderr) {
          return reject({ code: 500, message: grepStderr });
        }

        // Parse the output
        const processes = grepStdout.split('\n').filter(line => line).map(line => {
          const parts = line.trim().split(/\s+/);
          return {
            processId: parseInt(parts[1], 10),
            processString: line.trim(),
          };
        });

        resolve(processes);
      });
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