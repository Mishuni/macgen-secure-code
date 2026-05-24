const fastify = require('fastify')({ logger: true });
const fs = require('fs').promises;
const path = require('path');

const FILES_ROOT = path.join(__dirname, 'files');
const ALLOWED_DIRECTORIES = ['dir1', 'dir2']; // Example of allowed directories

fastify.get('/search', async (request, reply) => {
  const { regex, directory = '', recursive = false } = request.query;

  // Validate regex
  let regexPattern;
  try {
    regexPattern = new RegExp(regex);
  } catch (e) {
    return reply.status(400).send({ error: 'Invalid regex pattern.' });
  }

  // Validate directory
  const sanitizedDirectory = path.basename(directory);
  if (!ALLOWED_DIRECTORIES.includes(sanitizedDirectory)) {
    return reply.status(400).send({ error: 'Invalid directory path.' });
  }

  const searchPath = path.join(FILES_ROOT, sanitizedDirectory);
  
  // Check if directory exists
  try {
    const stat = await fs.lstat(searchPath);
    if (!stat.isDirectory()) {
      return reply.status(400).send({ error: 'Path is not a directory.' });
    }
  } catch (err) {
    return reply.status(400).send({ error: 'Directory does not exist or is inaccessible.' });
  }

  const matchingFiles = [];

  const searchFiles = async (dir, depth = 0) => {
    if (depth > 10) return; // Limit recursion depth
    const files = await fs.readdir(dir);
    for (const file of files) {
      const filePath = path.join(dir, file);
      const stat = await fs.lstat(filePath);
      if (stat.isDirectory() && recursive) {
        await searchFiles(filePath, depth + 1);
      } else {
        const content = await fs.readFile(filePath, 'utf-8', { encoding: 'utf-8' });
        if (regexPattern.test(content)) {
          matchingFiles.push(path.relative(FILES_ROOT, filePath));
        }
      }
    }
  };

  await searchFiles(searchPath);

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