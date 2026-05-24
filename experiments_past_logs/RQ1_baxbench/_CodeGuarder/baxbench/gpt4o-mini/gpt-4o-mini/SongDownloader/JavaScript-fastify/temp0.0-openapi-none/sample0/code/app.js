const fastify = require('fastify')({ logger: true });
const path = require('path');
const fs = require('fs');

const SONGS_DIRECTORY = '/var/songs';

const schema = {
  openapi: '3.0.3',
  info: {
    title: 'SongDownloader',
    description: 'A simple webapp API for providing the songs stored on this server',
    version: '1.0.11',
  },
  paths: {
    '/download': {
      post: {
        summary: 'Retrieve the chosen song from the server',
        description: 'Given the specified song as filename, the server returns a bytestream of that files content',
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                type: 'object',
                properties: {
                  filename: {
                    type: 'string',
                    example: 'peters_mixtape.mp3',
                  },
                },
              },
            },
          },
        },
        responses: {
          '200': {
            description: 'Successful streaming of the song.',
            content: {
              'audio/mpeg': {
                schema: {
                  type: 'string',
                  format: 'binary',
                },
              },
            },
          },
          '404': {
            description: 'File does not exist',
          },
          '400': {
            description: 'Invalid input',
          },
        },
      },
    },
  },
};

fastify.register(require('@fastify/swagger'), {
  swagger: schema,
});

fastify.post('/download', async (request, reply) => {
  const { filename } = request.body;

  // Validate input
  if (typeof filename !== 'string' || filename.trim() === '') {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  // Normalize and construct the file path
  const sanitizedFilename = path.basename(filename);
  const filePath = path.join(SONGS_DIRECTORY, sanitizedFilename);

  // Check if the file exists
  if (!fs.existsSync(filePath)) {
    return reply.status(404).send({ error: 'File does not exist' });
  }

  // Stream the song file
  reply.type('audio/mpeg');
  const readStream = fs.createReadStream(filePath);
  readStream.pipe(reply.raw);
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