import fastify from 'fastify';
import { exec } from 'child_process';
import util from 'util';

const app = fastify();
const execPromise = util.promisify(exec);

app.post('/monitor/commands', async (request, reply) => {
  const { filter_flags = '', command_regex } = request.body;

  if (!command_regex) {
    return reply.status(400).send({
      code: 400,
      message: 'command_regex is required'
    });
  }

  try {
    // Execute the 'ps' command with the provided filter flags
    const { stdout } = await execPromise(`ps ${filter_flags}`);
    const lines = stdout.split('\n').slice(1); // Skip the header line
    const regex = new RegExp(command_regex);
    const processes = lines
      .map(line => line.trim().split(/\s+/, 4))
      .filter(parts => parts.length >= 4 && regex.test(parts.slice(3).join(' ')))
      .map(parts => ({
        processId: parseInt(parts[0], 10),
        processString: parts.slice(3).join(' ')
      }));

    return reply.status(200).send(processes);
  } catch (error) {
    return reply.status(500).send({
      code: 500,
      message: 'Internal Server Error'
    });
  }
});

app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});