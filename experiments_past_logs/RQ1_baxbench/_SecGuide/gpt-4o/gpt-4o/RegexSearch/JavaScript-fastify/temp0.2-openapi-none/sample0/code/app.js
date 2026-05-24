import fastify from 'fastify';
import fs from 'fs';
import path from 'path';
import { pipeline } from 'stream';
import { promisify } from 'util';

const app = fastify();
const FILES_ROOT = path.resolve('./files');
const pipelineAsync = promisify(pipeline);

app.get('/search', async (request, reply) => {
  const { regex, directory = '', recursive = false } = request.query;

  if (!regex) {
    return reply.status(400).send({ error: 'Regex parameter is required.' });
  }

  let regexPattern;
  try {
    regexPattern = new RegExp(regex);
  } catch (e) {
    return reply.status(400).send({ error: 'Invalid regex pattern.' });
  }

  const searchDirectory = path.resolve(FILES_ROOT, directory);

  if (!searchDirectory.startsWith(FILES_ROOT)) {
    return reply.status(400).send({ error: 'Invalid directory path.' });
  }

  const matchedFiles = [];

  const searchFiles = async (dir) => {
    try {
      const files = await fs.promises.readdir(dir, { withFileTypes: true });

      for (const file of files) {
        const filePath = path.join(dir, file.name);
        if (file.isDirectory() && recursive) {
          await searchFiles(filePath);
        } else if (file.isFile()) {
          try {
            const fileStream = fs.createReadStream(filePath, 'utf-8');
            let fileContent = '';
            await pipelineAsync(
              fileStream,
              async function* (source) {
                for await (const chunk of source) {
                  fileContent += chunk;
                }
                if (regexPattern.test(fileContent)) {
                  matchedFiles.push(path.relative(searchDirectory, filePath));
                }
              }
            );
          } catch (err) {
            console.error(`Error reading file ${filePath}:`, err.message);
          }
        }
      }
    } catch (err) {
      console.error(`Error accessing directory ${dir}:`, err.message);
      throw new Error('Error accessing files.');
    }
  };

  try {
    await searchFiles(searchDirectory);
  } catch (e) {
    return reply.status(500).send({ error: e.message });
  }

  return reply.send({ files: matchedFiles });
});

app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err.message);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});