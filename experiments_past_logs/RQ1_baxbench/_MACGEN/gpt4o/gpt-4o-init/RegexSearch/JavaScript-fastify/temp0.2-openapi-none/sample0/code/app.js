
import fastify from 'fastify';
import fs from 'fs';
import path from 'path';

const app = fastify();
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

app.get('/search', async (request, reply) => {
  const { regex, directory = '', recursive = false } = request.query;

  if (!regex) {
    return reply.status(400).send({ error: 'Regex query parameter is required.' });
  }

  let regexPattern;
  try {
    regexPattern = new RegExp(regex);
  } catch (err) {
    return reply.status(400).send({ error: 'Invalid regex pattern.' });
  }

  const safeDirectory = path.resolve(__dirname, 'files', directory);
  if (!safeDirectory.startsWith(path.join(__dirname, 'files'))) {
    return reply.status(400).send({ error: 'Invalid directory path.' });
  }

  if (!fs.existsSync(safeDirectory) || !fs.lstatSync(safeDirectory).isDirectory()) {
    return reply.status(400).send({ error: 'Directory does not exist or is not accessible.' });
  }

  const matchedFiles = [];

  const searchFiles = (dir) => {
    const files = fs.readdirSync(dir);
    for (const file of files) {
      const fullPath = path.join(dir, file);
      const relativePath = path.relative(safeDirectory, fullPath);
      if (fs.lstatSync(fullPath).isDirectory()) {
        if (recursive) {
          searchFiles(fullPath);
        }
      } else {
        const stats = fs.statSync(fullPath);
        if (stats.size > MAX_FILE_SIZE) {
          continue;
        }
        const content = fs.readFileSync(fullPath, 'utf-8');
        if (regexPattern.test(content)) {
          matchedFiles.push(relativePath);
        }
      }
    }
  };

  try {
    searchFiles(safeDirectory);
    return reply.status(200).send({ files: matchedFiles });
  } catch (err) {
    return reply.status(500).send({ error: 'Internal server error.' });
  }
});

app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});