const fastify = require('fastify')({ logger: true });
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');

fastify.post('/compile', async (request, reply) => {
  const { fileName, fileContent } = request.body;

  if (!fileName || !fileContent) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  const fileExtension = path.extname(fileName);
  const allowedExtensions = ['.ts', '.cpp'];

  if (!allowedExtensions.includes(fileExtension) || fileName.includes('..')) {
    return reply.status(400).send({ error: 'Unsupported file type or invalid file name' });
  }

  const tempFilePath = path.join(__dirname, fileName);

  try {
    fs.writeFileSync(tempFilePath, fileContent);

    let compileCommand;
    if (fileExtension === '.ts') {
      compileCommand = 'tsc';
    } else if (fileExtension === '.cpp') {
      compileCommand = 'g++';
    }

    execFile(compileCommand, [tempFilePath], (error, stdout, stderr) => {
      fs.unlinkSync(tempFilePath); // Clean up the temporary file
      if (fileExtension === '.cpp') {
        try {
          fs.unlinkSync(`${tempFilePath}.out`); // Clean up the output file if it exists
        } catch (err) {
          // Ignore if the output file doesn't exist
        }
      }

      if (error) {
        return reply.send({ hasError: true, compilerError: stderr });
      }

      return reply.send({ hasError: false, compilerError: null });
    });
  } catch (err) {
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