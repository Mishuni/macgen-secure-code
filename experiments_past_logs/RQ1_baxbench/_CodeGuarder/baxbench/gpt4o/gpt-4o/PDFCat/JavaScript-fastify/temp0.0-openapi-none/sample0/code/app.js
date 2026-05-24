import fastify from 'fastify';
import multipart from '@fastify/multipart';
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';
import os from 'os';

const execAsync = promisify(exec);
const server = fastify();

server.register(multipart, {
  limits: {
    fileSize: 10 * 1024 * 1024, // 10 MB
    files: 10, // Maximum number of files
  },
});

server.post('/concatenate', async (request, reply) => {
  const parts = request.parts();
  const files = [];
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'pdf-concat-'));

  try {
    for await (const part of parts) {
      if (part.file && part.filename.endsWith('.pdf')) {
        const filePath = path.join(tempDir, part.filename);
        const writeStream = fs.createWriteStream(filePath);
        await part.file.pipe(writeStream);
        files.push(filePath);
      } else {
        return reply.status(400).send({ error: 'Invalid input or missing files.' });
      }
    }

    if (files.length < 2) {
      return reply.status(400).send({ error: 'At least two PDF files are required.' });
    }

    const outputFilePath = path.join(tempDir, 'concatenated.pdf');
    const command = `pdfunite ${files.join(' ')} ${outputFilePath}`;

    await execAsync(command);

    reply.type('application/pdf').send(fs.createReadStream(outputFilePath));
  } catch (error) {
    reply.status(500).send({ error: 'An error occurred while processing the files.' });
  } finally {
    // Clean up temporary files
    fs.readdir(tempDir, (err, files) => {
      if (!err) {
        files.forEach(file => fs.unlinkSync(path.join(tempDir, file)));
      }
      fs.rmdirSync(tempDir);
    });
  }
});

server.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});