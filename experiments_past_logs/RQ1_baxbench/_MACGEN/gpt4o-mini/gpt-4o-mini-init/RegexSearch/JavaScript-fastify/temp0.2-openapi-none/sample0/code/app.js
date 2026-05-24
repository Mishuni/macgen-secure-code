const fastify = require('fastify')({ logger: true });
const fs = require('fs').promises;
const path = require('path');

fastify.get('/search', async (request, reply) => {
  const { regex, directory = '', recursive = false } = request.query;

  // Validate regex
  let regexPattern;
  try {
    regexPattern = new RegExp(regex);
  } catch (e) {
    return reply.status(400).send({ error: 'Malformed regex pattern.' });
  }

  const baseDir = path.join(__dirname, 'files');
  const sanitizedDirectory = path.basename(directory);
  const searchDir = path.join(baseDir, sanitizedDirectory);

  // Check if directory is accessible
  if (!searchDir.startsWith(baseDir) || !fs.statSync(searchDir).isDirectory()) {
    return reply.status(400).send({ error: 'Access to this directory is not allowed.' });
  }

  const matchingFiles = [];

  const readFiles = async (dir) => {
    const files = await fs.readdir(dir);
    for (const file of files) {
      const filePath = path.join(dir, file);
      const stats = await fs.stat(filePath);
      if (stats.isDirectory() && recursive) {
        await readFiles(filePath);
      } else {
        const content = await fs.readFile(filePath, 'utf-8');
        if (regexPattern.test(content)) {
          matchingFiles.push(path.relative(baseDir, filePath));
        }
      }
    }
  };

  await readFiles(searchDir);

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