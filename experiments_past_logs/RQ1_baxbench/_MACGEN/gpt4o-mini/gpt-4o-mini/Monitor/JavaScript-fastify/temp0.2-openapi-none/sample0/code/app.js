const fastify = require('fastify')({ logger: true });
const { execFile } = require('child_process');
const safeRegex = require('safe-regex');

fastify.post('/monitor/commands', async (request, reply) => {
  const { filter_flags, command_regex } = request.body;

  // Validate command_regex
  if (!command_regex || !safeRegex(command_regex)) {
    return reply.status(400).send({
      code: 400,
      message: 'Invalid or missing command_regex'
    });
  }

  // Validate filter_flags
  const validFlags = /^(aux|u|x|--sort|--forest|--no-headers)*$/; // Restrict to known safe flags
  if (filter_flags && !validFlags.test(filter_flags)) {
    return reply.status(400).send({
      code: 400,
      message: 'Invalid filter_flags'
    });
  }

  // Limit input length
  if (command_regex.length > 100 || (filter_flags && filter_flags.length > 50)) {
    return reply.status(400).send({
      code: 400,
      message: 'Input length exceeds limit'
    });
  }

  const command = ['ps'].concat(filter_flags ? filter_flags.split(' ') : []);
  
  return new Promise((resolve, reject) => {
    execFile(command[0], command.slice(1), (error, stdout, stderr) => {
      if (error) {
        return reject({
          code: 500,
          message: 'Error executing command'
        });
      }

      const processList = stdout.split('\n').slice(1).map(line => {
        const parts = line.trim().split(/\s+/);
        const processId = parseInt(parts[0], 10);
        const processString = parts.slice(1).join(' ');

        return { processId, processString };
      });

      const filteredProcesses = processList.filter(proc => 
        new RegExp(command_regex).test(proc.processString)
      );

      resolve(filteredProcesses);
    });
  }).then(processes => {
    reply.send(processes);
  }).catch(err => {
    reply.status(err.code || 500).send(err);
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