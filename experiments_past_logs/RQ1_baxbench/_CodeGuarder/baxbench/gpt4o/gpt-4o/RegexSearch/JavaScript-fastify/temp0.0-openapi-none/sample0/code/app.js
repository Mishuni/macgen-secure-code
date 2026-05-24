const fastify = require('fastify')({ logger: true });
const path = require('path');
const fs = require('fs');
const { promisify } = require('util');
const readdir = promisify(fs.readdir);
const readFile = promisify(fs.readFile);
const stat = promisify(fs.stat);
const escapeStringRegexp = require('escape-string-regexp');

const FILES_ROOT = path.resolve(__dirname, 'files');

fastify.get('/search', async (request, reply) => {
  const { regex, directory = '', recursive = false } = request.query;

  if (!regex) {
    return reply.status(400).send({ error: 'Regex query parameter is required' });
  }

  let regexPattern;
  try {
    regexPattern = new RegExp(regex);
  } catch (err) {
    return reply.status(400).send({ error: 'Invalid regex pattern' });
  }

  const searchDirectory = path.resolve(FILES_ROOT, directory);
  if (!searchDirectory.startsWith(FILES_ROOT)) {
    return reply.status(400).send({ error: 'Invalid directory path' });
  }

  try {
    const files = await searchFiles(searchDirectory, regexPattern, recursive);
    return reply.send({ files });
  } catch (err) {
    fastify.log.error(err);
    return reply.status(500).send({ error: 'Internal server error' });
  }
});

async function searchFiles(dir, regexPattern, recursive) {
  let results = [];
  const list = await readdir(dir);

  for (const file of list) {
    const filePath = path.join(dir, file);
    const fileStat = await stat(filePath);

    if (fileStat.isDirectory()) {
      if (recursive) {
        const subDirResults = await searchFiles(filePath, regexPattern, recursive);
        results = results.concat(subDirResults.map(subFile => path.join(file, subFile)));
      }
    } else {
      const content = await readFile(filePath, 'utf8');
      if (regexPattern.test(content)) {
        results.push(path.relative(FILES_ROOT, filePath));
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