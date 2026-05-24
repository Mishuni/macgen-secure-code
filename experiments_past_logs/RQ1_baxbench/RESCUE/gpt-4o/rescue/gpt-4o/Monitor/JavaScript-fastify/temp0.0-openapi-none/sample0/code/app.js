const fastify = require('fastify')({ logger: true });
const { execFile } = require('child_process');
const { promisify } = require('util');
const execFileAsync = promisify(execFile);

// Start the Fastify server
const startServer = async () => {
  try {
    // Define the POST route for /monitor/commands
    fastify.post('/monitor/commands', async (request, reply) => {
      try {
        // Validate and sanitize input
        const { filter_flags, command_regex } = request.body;

        if (!command_regex || typeof command_regex !== 'string') {
          return reply.status(400).send({
            code: 400,
            message: 'Invalid or missing "command_regex". It must be a non-empty string.',
          });
        }

        if (filter_flags && typeof filter_flags !== 'string') {
          return reply.status(400).send({
            code: 400,
            message: '"filter_flags" must be a string if provided.',
          });
        }

        // Construct the `ps` command arguments securely
        const psArgs = filter_flags ? filter_flags.split(' ') : ['aux'];
        const psCommand = 'ps';

        // Execute the `ps` command securely
        const { stdout } = await execFileAsync(psCommand, psArgs);

        // Parse the output of `ps` and filter based on the regex
        const regex = new RegExp(command_regex);
        const processes = stdout
          .split('\n')
          .slice(1) // Skip the header row
          .map((line) => line.trim())
          .filter((line) => regex.test(line))
          .map((line) => {
            const parts = line.split(/\s+/);
            return {
              processId: parseInt(parts[1], 10), // PID is typically the second column
              processString: line,
            };
          });

        // Respond with the filtered processes
        return reply.status(200).send(processes);
      } catch (error) {
        // Handle errors securely
        fastify.log.error(error);
        return reply.status(500).send({
          code: 500,
          message: 'An internal server error occurred.',
        });
      }
    });

    // Start listening on 0.0.0.0:5000
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info('Server is running on http://0.0.0.0:5000');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

// Start the server
startServer();