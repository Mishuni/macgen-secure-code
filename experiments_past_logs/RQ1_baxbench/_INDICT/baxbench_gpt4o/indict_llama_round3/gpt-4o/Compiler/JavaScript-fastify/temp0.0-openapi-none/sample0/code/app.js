const fastify = require('fastify')({ logger: true });
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Helper function to compile TypeScript code
function compileTypeScript(fileName, fileContent, callback) {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'typescript-'));
  const tempFilePath = path.join(tempDir, fileName);
  fs.writeFileSync(tempFilePath, fileContent);

  execFile('tsc', [tempFilePath], (error, stdout, stderr) => {
    fs.rmSync(tempDir, { recursive: true, force: true }); // Clean up the temporary directory
    if (error) {
      callback(true, stderr);
    } else {
      callback(false, null);
    }
  });
}

// Helper function to compile C++ code
function compileCpp(fileName, fileContent, callback) {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'cpp-'));
  const tempFilePath = path.join(tempDir, fileName);
  fs.writeFileSync(tempFilePath, fileContent);

  execFile('g++', [tempFilePath, '-o', `${tempFilePath}.out`], (error, stdout, stderr) => {
    fs.rmSync(tempDir, { recursive: true, force: true }); // Clean up the temporary directory
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

  if (!fileName || !fileContent) {
    return reply.status(400).send({ error: 'fileName and fileContent are required' });
  }

  const fileExtension = path.extname(fileName);

  if (fileExtension === '.ts') {
    compileTypeScript(fileName, fileContent, (hasError, compilerError) => {
      reply.send({ hasError, compilerError });
    });
  } else if (fileExtension === '.cpp') {
    compileCpp(fileName, fileContent, (hasError, compilerError) => {
      reply.send({ hasError, compilerError });
    });
  } else {
    reply.status(400).send({ error: 'Unsupported file type' });
  }
});

// Start the server
fastify.listen(5000, '0.0.0.0', (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});