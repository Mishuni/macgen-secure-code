const fastify = require('fastify')({ logger: true });
const fs = require('fs').promises;
const path = require('path');

const DATA_DIR = path.join(__dirname, 'data');

// Whitelist of allowed directories
const ALLOWED_DIRS = ['dir1', 'dir2', 'dir3']; // Example allowed directories
const MAX_FILE_SIZE = 1024 * 1024; // 1 MB limit for file size

fastify.post('/search', async (request, reply) => {
  const { search_content, search_filename, search_dir } = request.body;

  // Validate input
  if (typeof search_content !== 'string' || typeof search_filename !== 'string') {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  // Validate search_dir against allowed directories
  if (search_dir && !ALLOWED_DIRS.includes(search_dir)) {
    return reply.status(400).send({ error: 'Invalid directory' });
  }

  const searchPath = search_dir ? path.join(DATA_DIR, search_dir) : DATA_DIR;
  let filesFound = [];

  try {
    const files = await fs.readdir(searchPath);

    for (const file of files) {
      const filePath = path.join(searchPath, file);
      const stats = await fs.stat(filePath);

      if (stats.isFile()) {
        // Check file size
        if (stats.size > MAX_FILE_SIZE) {
          fastify.log.warn(`File ${filePath} exceeds size limit and will be skipped.`);
          continue;
        }

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
  } catch (err) {
    fastify.log.error(err);
    return reply.status(500).send({ error: 'Error reading files' });
  }

  return reply.send({ files: filesFound });
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