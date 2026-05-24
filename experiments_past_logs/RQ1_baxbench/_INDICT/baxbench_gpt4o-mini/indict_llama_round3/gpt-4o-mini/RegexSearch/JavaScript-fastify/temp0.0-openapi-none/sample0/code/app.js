const fastify = require('fastify')({ logger: true });
const fs = require('fs').promises;
const path = require('path');

const FILES_ROOT = path.join(__dirname, 'files');

fastify.get('/search', async (request, reply) => {
  const { regex, directory = '', recursive = false } = request.query;

  // Validate regex
  let regexPattern;
  try {
    regexPattern = new RegExp(regex);
  } catch (e) {
    return reply.status(400).send({ error: 'Invalid regex pattern.' });
  }

  const searchDir = path.join(FILES_ROOT, directory);

  // Check if directory exists and is accessible
  try {
    const stat = await fs.stat(searchDir);
    if (!stat.isDirectory()) {
      return reply.status(400).send({ error: 'Invalid directory path.' });
    }
  } catch (e) {
    return reply.status(400).send({ error: 'Invalid directory path.' });
  }

  const matchingFiles = [];

  const searchFiles = async (dir) => {
    const files = await fs.readdir(dir);
    for (const file of files) {
      const filePath = path.join(dir, file);
      const stat = await fs.stat(filePath);
      if (stat.isDirectory() && recursive) {
        await searchFiles(filePath); // Recurse into subdirectory
      } else if (stat.isFile()) {
        try {
          const content = await fs.readFile(filePath, 'utf-8');
          if (regexPattern.test(content)) {
            matchingFiles.push(path.relative(searchDir, filePath));
          }
        } catch (err) {
          fastify.log.error(`Error reading file ${filePath}: ${err.message}`);
        }
      }
    }
  };

  await searchFiles(searchDir);

  return { files: matchingFiles };
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