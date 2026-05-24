const fastify = require('fastify')({ logger: true });
const { exec } = require('child_process');

// Set up the Fastify server
fastify.register(require('@fastify/multipart'));

// Define the /compile endpoint
fastify.post('/compile', async (request, reply) => {
  try {
    // Parse and validate request body
    const contentType = request.headers['content-type'];
    if (!contentType || !contentType.includes('application/json')) {
      return reply.status(400).send({ error: 'Invalid Content-Type' });
    }

    const { fileName, fileContent } = request.body;
    if (!fileName || !fileContent) {
      return reply.status(400).send({ error: 'Invalid request body' });
    }

    // Determine language and compile code
    let compileCommand;
    if (fileName.endsWith('.ts')) {
      compileCommand = `tsc --noEmit --skipLibCheck ${fileName}`;
    } else if (fileName.endsWith('.cpp')) {
      compileCommand = `g++ -fsyntax-only ${fileName}`;
    } else {
      return reply.status(400).send({ error: 'Unsupported file type' });
    }

    // Capture compilation output
    exec(compileCommand, (error, stdout, stderr) => {
      if (error) {
        // Format and send response
        return reply.send({
          hasError: true,
          compilerError: stderr || stdout,
        });
      }
      reply.send({
        hasError: false,
        compilerError: null,
      });
    });
  } catch (err) {
    // Error handling
    fastify.log.error(err);
    reply.status(500).send({ error: 'Internal Server Error' });
  }
});

// Start the Fastify server
fastify.listen(5000, '0.0.0.0', (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});