const fastify = require('fastify')({ logger: true });
const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const tmp = require('tmp');

// Utility function to compile TypeScript code
function compileTypeScript(filePath, callback) {
  execFile('tsc', [filePath], (error, stdout, stderr) => {
    if (error) {
      callback(true, stderr);
    } else {
      callback(false, null);
    }
  });
}

// Utility function to compile C++ code
function compileCpp(filePath, callback) {
  execFile('g++', [filePath, '-o', `${filePath}.out`], (error, stdout, stderr) => {
    if (error) {
      callback(true, stderr);
    } else {
      callback(false, null);
    }
  });
}

// Route to handle compilation requests
fastify.post('/compile', async (request, reply) => {
  const { fileName, fileContent } = request.body;

  // Validate input
  if (!fileName || !fileContent) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  // Validate fileName to prevent directory traversal
  if (path.basename(fileName) !== fileName || /[<>:"/\\|?*\x00-\x1F]/.test(fileName)) {
    return reply.status(400).send({ error: 'Invalid file name' });
  }

  // Determine file extension
  const ext = path.extname(fileName).toLowerCase();
  if (ext !== '.ts' && ext !== '.cpp') {
    return reply.status(400).send({ error: 'Unsupported file type' });
  }

  // Validate file content (basic validation to prevent empty content)
  if (typeof fileContent !== 'string' || fileContent.trim() === '') {
    return reply.status(400).send({ error: 'Invalid file content' });
  }

  // Create a secure temporary file
  tmp.file({ postfix: ext, mode: 0o600 }, (err, filePath, fd, cleanupCallback) => {
    if (err) {
      return reply.status(500).send({ error: 'Failed to create temporary file' });
    }

    // Write the file content to the temporary file
    fs.write(fd, fileContent, (writeErr) => {
      if (writeErr) {
        cleanupCallback();
        return reply.status(500).send({ error: 'Failed to write to temporary file' });
      }

      // Compile based on file extension
      const compileCallback = (hasError, compilerError) => {
        cleanupCallback(); // Clean up the temporary file
        reply.send({ hasError, compilerError });
      };

      if (ext === '.ts') {
        compileTypeScript(filePath, compileCallback);
      } else if (ext === '.cpp') {
        compileCpp(filePath, compileCallback);
      }
    });
  });
});

// Start the server
fastify.listen(5000, '127.0.0.1', (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});