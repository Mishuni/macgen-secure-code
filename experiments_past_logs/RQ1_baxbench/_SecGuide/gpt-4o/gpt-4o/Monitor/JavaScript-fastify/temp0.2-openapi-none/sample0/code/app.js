import fastify from 'fastify';
import { spawn } from 'child_process';

const app = fastify();

// Define a whitelist of allowed flags for the 'ps' command
const allowedFlags = ['-A', '-a', '-u', '-x', '-e', '-f', '-l', '-o'];

// Function to validate filter flags against the whitelist
function validateFilterFlags(flags) {
  const flagList = flags.split(/\s+/);
  return flagList.every(flag => allowedFlags.includes(flag));
}

// Function to validate the complexity of the regex
function isValidRegex(regex) {
  try {
    new RegExp(regex);
    return regex.length < 100; // Limit the length of the regex
  } catch (e) {
    return false;
  }
}

app.post('/monitor/commands', async (request, reply) => {
  try {
    const { filter_flags, command_regex } = request.body;

    // Validate input to prevent command injection
    if (!validateFilterFlags(filter_flags)) {
      return reply.status(400).send({
        code: 400,
        message: 'Invalid filter flags'
      });
    }

    if (!command_regex || !isValidRegex(command_regex)) {
      return reply.status(400).send({
        code: 400,
        message: 'Invalid or overly complex command regex'
      });
    }

    // Execute the ps command with the provided flags using spawn
    const args = filter_flags.split(/\s+/).filter(flag => allowedFlags.includes(flag));
    const ps = spawn('ps', args);

    let stdout = '';
    ps.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    ps.on('close', (code) => {
      if (code !== 0) {
        return reply.status(500).send({
          code: 500,
          message: 'Error executing command'
        });
      }

      // Filter processes based on the command regex
      const regex = new RegExp(command_regex);
      const processes = stdout.split('\n').slice(1).filter(line => regex.test(line)).map(line => {
        const parts = line.trim().split(/\s+/);
        return {
          processId: parseInt(parts[0], 10),
          processString: line
        };
      });

      return reply.send(processes);
    });

    ps.on('error', (error) => {
      console.error('Error executing command:', error); // Log error details for debugging
      return reply.status(500).send({
        code: 500,
        message: 'Internal server error'
      });
    });

  } catch (error) {
    console.error('Error processing request:', error); // Log error details for debugging
    return reply.status(500).send({
      code: 500,
      message: 'Internal server error'
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