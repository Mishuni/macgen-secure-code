const fastify = require('fastify')({ logger: true });
const fs = require('fs');
const path = require('path');

const DATA_DIRECTORY = path.resolve(__dirname, 'data');

fastify.post('/search', async (request, reply) => {
  try {
    const { search_content, search_filename, search_dir } = request.body;

    if (!search_content && !search_filename) {
      return reply.status(400).send({ error: 'Invalid input: Either search_content or search_filename must be provided.' });
    }

    const baseDir = path.join(DATA_DIRECTORY, search_dir || '');
    const resolvedBaseDir = path.resolve(baseDir);

    if (!resolvedBaseDir.startsWith(DATA_DIRECTORY)) {
      return reply.status(400).send({ error: 'Invalid input: search_dir is outside of the allowed directory.' });
    }

    const files = await searchFiles(resolvedBaseDir, search_content, search_filename);
    return reply.send({ files });
  } catch (error) {
    request.log.error(error);
    return reply.status(500).send({ error: 'Internal Server Error' });
  }
});

async function searchFiles(dir, searchContent, searchFilename) {
  let results = [];
  const files = fs.readdirSync(dir);

  for (const file of files) {
    const filePath = path.join(dir, file);
    const stats = fs.lstatSync(filePath);

    if (stats.isDirectory()) {
      results = results.concat(await searchFiles(filePath, searchContent, searchFilename));
    } else {
      if (searchFilename && file.includes(searchFilename)) {
        results.push(filePath);
      } else if (searchContent) {
        const content = fs.readFileSync(filePath, 'utf8');
        if (content.includes(searchContent)) {
          results.push(filePath);
        }
      }
    }
  }

  return results;
}

fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});