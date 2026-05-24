const fastify = require('fastify')();
const { execFile } = require('child_process');

const safeFilterFlags = ['aux', 'aux -T', 'x'];

fastify.post('/monitor/commands', async (request, reply) => {
  const { filter_flags = '', command_regex } = request.body;

  if (!command_regex) {
    return reply.status(400).send({
      code: 400,
      message: 'command_regex is required'
    });
  }

  if (!safeFilterFlags.includes(filter_flags)) {
    return reply.status(400).send({
      code: 400,
      message: 'Invalid filter_flags'
    });
  }

  let regex;
  try {
    regex = new RegExp(command_regex);
  } catch (e) {
    return reply.status(400).send({
      code: 400,
      message: 'Invalid command_regex'
    });
  }

  execFile('ps', [filter_flags], (error, stdout, stderr) => {
    if (error) {
      return reply.status(500).send({
        code: 500,
        message: 'Error executing ps command'
      });
    }

    const processes = stdout.split('\n').slice(1).filter(line => regex.test(line)).map(line => {
      const parts = line.trim().split(/\s+/);
      return {
        processId: parseInt(parts[0], 10),
        processString: line
      };
    });

    reply.send(processes);
  });
});

fastify.listen({ port: 5000, host: '0.0.0.0' }, err => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log('Server listening on http://0.0.0.0:5000');
});