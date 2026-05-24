import fastify from 'fastify';
import fs from 'fs';
import path from 'path';

const app = fastify();

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

  const rootDir = path.join(__dirname, 'files');
  const searchDir = path.join(rootDir, directory);

  if (!searchDir.startsWith(rootDir)) {
    return reply.status(400).send({ error: 'Invalid directory path.' });
  }

  if (!fs.existsSync(searchDir)) {
    return reply.status(400).send({ error: 'Directory does not exist.' });
  }

  const matchedFiles = [];

  const searchFiles = (dir) => {
    const files = fs.readdirSync(dir);

    for (const file of files) {
      const fullPath = path.join(dir, file);
      const relativePath = path.relative(rootDir, fullPath);

      if (fs.statSync(fullPath).isDirectory()) {
        if (recursive) {
          searchFiles(fullPath);
        }
      } else {
        try {
          const fileContent = fs.readFileSync(fullPath, 'utf-8');
          if (regexPattern.test(fileContent)) {
            matchedFiles.push(relativePath);
          }
        } catch (err) {
          console.error(`Error reading file ${fullPath}:`, err);
        }
      }
    }
  };

  try {
    searchFiles(searchDir);
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