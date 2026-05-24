const fastify = require('fastify')({ logger: true });
const fs = require('fs').promises;
const path = require('path');

const DATA_DIR = path.join(__dirname, 'data');

fastify.post('/search', async (request, reply) => {
  const { search_content, search_filename, search_dir } = request.body;

  if (!search_content && !search_filename) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  // Validate search_dir to prevent directory traversal attacks
  if (search_dir) {
    const resolvedDir = path.join(DATA_DIR, search_dir);
    if (!resolvedDir.startsWith(DATA_DIR) || !resolvedDir.includes(DATA_DIR)) {
      return reply.status(400).send({ error: 'Invalid directory' });
    }
  }

  const searchPath = search_dir ? path.join(DATA_DIR, search_dir) : DATA_DIR;

  try {
    const files = await fs.readdir(searchPath);
    const filesFound = [];

    for (const file of files) {
      const filePath = path.join(searchPath, file);
      const stats = await fs.stat(filePath);

      if (stats.isFile()) {
        let contentMatches = true;
        let filenameMatches = true;

        if (search_content) {
          const fileContent = await fs.readFile(filePath, 'utf-8');
          contentMatches = fileContent.includes(search_content);
        }

        if (search_filename) {
          filenameMatches = file.startsWith(search_filename);
        }

        if (contentMatches || filenameMatches) {
          filesFound.push(filePath);
        }
      }
    }

    return { files: filesFound };
  } catch (error) {
    return reply.status(400).send({ error: 'Invalid input or directory does not exist' });
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