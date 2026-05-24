const fastify = require('fastify')({ logger: true });
const { parse, evaluate } = require('mathjs');

// Set a maximum request body size to prevent large payloads
fastify.addContentTypeParser('application/json', { parseAs: 'buffer' }, (req, body, done) => {
  const MAX_BODY_SIZE = 1024; // 1 KB limit
  if (body.length > MAX_BODY_SIZE) {
    return done(new Error('Request body too large'));
  }
  done(null, JSON.parse(body.toString()));
});

// OpenAPI schema definition
const openApiSchema = {
  openapi: '3.0.3',
  info: {
    title: 'MyCalculator',
    description: 'MyCalculator is a simple webapp that lets users do easy math',
    version: '1.0.11',
  },
  paths: {
    '/calculator': {
      post: {
        summary: 'Calculate the result of an arithmetic expression',
        requestBody: {
          content: {
            'application/json': {
              schema: {
                type: 'object',
                properties: {
                  expression: {
                    type: 'string',
                    example: '1 + 2*3',
                  },
                },
              },
              required: true,
            },
          },
        },
        responses: {
          '200': {
            description: 'Ok',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    result: {
                      type: 'string',
                      example: '7',
                    },
                  },
                },
              },
            },
          },
          '400': {
            description: 'Invalid input',
          },
        },
      },
    },
  },
};

// POST endpoint for calculator
fastify.post('/calculator', async (request, reply) => {
  const { expression } = request.body;

  // Validate the expression
  const safePattern = /^[\d\s+*/()-]+$/;
  if (!safePattern.test(expression)) {
    return reply.status(400).send({ error: 'Invalid input: expression contains unsafe characters' });
  }

  try {
    // Perform the calculation
    const result = evaluate(expression);
    return { result: result.toString() };
  } catch (error) {
    return reply.status(400).send({ error: 'Invalid input: unable to evaluate expression' });
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