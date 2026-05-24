const fastify = require('fastify')({ logger: true });
const fs = require('fs');
const path = require('path');

// Helper function to validate and sanitize input
function sanitizeInput(input) {
  if (typeof input !== 'string') return '';
  return input.replace(/[^a-zA-Z0-9_\-./]/g, '');
}

// Helper function to search files
function searchFiles(searchContent, searchFilename, searchDir) {
  const baseDir = path.join(__dirname, 'data');
  const targetDir = path.join(baseDir, sanitizeInput(searchDir || ''));

  // Ensure the target directory is within the base directory
  if (!path.resolve(targetDir).startsWith(path.resolve(baseDir))) {
    throw new Error('Invalid directory path');
  }

  let resultFiles = [];

  function searchInDirectory(directory) {
    const files = fs.readdirSync(directory);

    files.forEach(file => {
      const filePath = path.join(directory, file);
      const stat = fs.statSync(filePath);

      if (stat.isDirectory()) {
        searchInDirectory(filePath);
      } else {
        let match = false;

        if (searchFilename && file.startsWith(searchFilename)) {
          match = true;
        }

        if (searchContent) {
          const content = fs.readFileSync(filePath, 'utf8');
          if (content.includes(searchContent)) {
            match = true;
          }
        }

        if (match) {
          resultFiles.push(filePath);
        }
      }
    });
  }

  searchInDirectory(targetDir);
  return resultFiles;
}

// Define the /search route
fastify.post('/search', async (request, reply) => {
  const { search_content, search_filename, search_dir } = request.body;

  if (!search_content && !search_filename) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  try {
    const files = searchFiles(search_content, search_filename, search_dir);
    return reply.send({ files });
  } catch (error) {
    fastify.log.error(error);
    return reply.status(500).send({ error: 'Internal Server Error' });
  }
});

// Start the server
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