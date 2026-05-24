const fastify = require('fastify')({ logger: true });
const fs = require('fs');
const path = require('path');

const logFilePath = path.join(__dirname, 'logs.txt');

// OpenAPI schema
const openApiSchema = {
  openapi: '3.0.3',
  info: {
    title: 'LoggingAPI',
    description: 'A simple webapp API for logging functionality.',
    version: '1.0.11',
  },
  paths: {
    '/log': {
      post: {
        summary: 'Log a message',
        description: 'Log a message to the server.',
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                type: 'object',
                properties: {
                  message: {
                    type: 'string',
                  },
                },
                example: {
                  message: 'This is a log message',
                },
              },
            },
          },
          responses: {
            '200': {
              description: 'Log message successful',
            },
          },
        },
      },
    },
    '/logs': {
      get: {
        summary: 'Retrieve logs',
        description: 'Retrieve all logged messages.',
        responses: {
          '200': {
            description: 'Logs retrieved successfully',
            content: {
              'text/plain': {
                schema: {
                  type: 'string',
                },
              },
            },
          },
        },
      },
    },
  },
};

// POST endpoint to log messages
fastify.post('/log', async (request, reply) => {
  const { message } = request.body;

  if (typeof message !== 'string' || message.trim() === '') {
    return reply.status(400).send({ error: 'Invalid message' });
  }

  try {
    fs.appendFileSync(logFilePath, `${message}\n`, { flag: 'a' });
    return reply.status(200).send({ status: 'Message logged successfully' });
  } catch (error) {
    request.log.error(error);
    return reply.status(500).send({ error: 'Failed to log message' });
  }
});

// GET endpoint to retrieve logs
fastify.get('/logs', async (request, reply) => {
  try {
    const logs = fs.readFileSync(logFilePath, 'utf-8');
    return reply.type('text/plain').send(logs);
  } catch (error) {
    request.log.error(error);
    return reply.status(500).send({ error: 'Failed to retrieve logs' });
  }
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