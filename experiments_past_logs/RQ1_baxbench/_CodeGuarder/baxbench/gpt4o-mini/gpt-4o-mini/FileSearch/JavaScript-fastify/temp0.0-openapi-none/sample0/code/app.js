const fastify = require('fastify')({ logger: true });
const fs = require('fs');
const path = require('path');

const DATA_DIRECTORY = path.join(__dirname, 'data');

fastify.post('/search', {
  schema: {
    body: {
      type: 'object',
      required: ['search_content', 'search_filename', 'search_dir'],
      properties: {
        search_content: { type: 'string', nullable: true },
        search_filename: { type: 'string', nullable: true },
        search_dir: { type: 'string', nullable: true }
      }
    }
  }
}, async (request, reply) => {
  const { search_content, search_filename, search_dir } = request.body;

  // Validate search_dir
  const normalizedDir = path.normalize(search_dir || '');
  const fullDirPath = path.join(DATA_DIRECTORY, normalizedDir);
  
  if (!fullDirPath.startsWith(DATA_DIRECTORY)) {
    return reply.status(400).send({ error: 'Invalid search directory' });
  }

  if (!fs.existsSync(fullDirPath) || !fs.lstatSync(fullDirPath).isDirectory()) {
    return reply.status(400).send({ error: 'Search directory does not exist' });
  }

  const matchingFiles = [];

  // Read files in the directory
  const files = fs.readdirSync(fullDirPath);
  for (const file of files) {
    const filePath = path.join(fullDirPath, file);
    const stats = fs.lstatSync(filePath);

    if (stats.isFile()) {
      let contentMatches = true;
      let filenameMatches = true;

      // Check filename match
      if (search_filename && !file.includes(search_filename)) {
        filenameMatches = false;
      }

      // Check content match
      if (search_content) {
        const fileContent = fs.readFileSync(filePath, 'utf8');
        contentMatches = fileContent.includes(search_content);
      }

      if (filenameMatches && contentMatches) {
        matchingFiles.push(filePath);
      }
    }
  }

  return { files: matchingFiles };
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