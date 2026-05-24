
const fastify = require('fastify')({ logger: true });
const fs = require('fs');
const path = require('path');

fastify.post('/search', async (request, reply) => {
  const { search_content, search_filename, search_dir } = request.body;

  if (!search_content && !search_filename) {
    return reply.status(400).send({ error: 'Invalid input: Either search_content or search_filename must be provided.' });
  }

  if (search_content && search_content.length > 1000) {
    return reply.status(400).send({ error: 'Content too long.' });
  }

  if (search_filename && /[^a-zA-Z0-9_\-\.]/.test(search_filename)) {
    return reply.status(400).send({ error: 'Invalid filename characters.' });
  }

  const baseDir = path.resolve(__dirname, 'data');
  const searchPath = path.resolve(baseDir, search_dir || '');

  if (!searchPath.startsWith(baseDir)) {
    return reply.status(400).send({ error: 'Invalid directory access.' });
  }

  if (!fs.existsSync(searchPath) || !fs.lstatSync(searchPath).isDirectory()) {
    return reply.status(400).send({ error: 'Invalid input: search_dir does not exist or is not a directory.' });
  }

  const matchingFiles = [];

  const searchFiles = (dir) => {
    const files = fs.readdirSync(dir);
    for (const file of files) {
      const fullPath = path.join(dir, file);
      const stat = fs.lstatSync(fullPath);

      if (stat.isDirectory()) {
        searchFiles(fullPath);
      } else {
        let matches = false;

        if (search_filename && file.includes(search_filename)) {
          matches = true;
        }

        if (search_content) {
          const content = fs.readFileSync(fullPath, 'utf8');
          if (content.includes(search_content)) {
            matches = true;
          }
        }

        if (matches) {
          matchingFiles.push(fullPath);
        }
      }
    }
  };

  try {
    searchFiles(searchPath);
    return reply.send({ files: matchingFiles });
  } catch (error) {
    return reply.status(500).send({ error: 'Internal server error' });
  }
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