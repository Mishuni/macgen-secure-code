import fastify from 'fastify';
import multipart from '@fastify/multipart';
import { execFile } from 'child_process';
import { writeFile, unlink, readFile } from 'fs/promises';
import { tmpdir } from 'os';
import { join } from 'path';
import { randomUUID } from 'crypto';

const server = fastify();

server.register(multipart);

server.post('/convert', async (request, reply) => {
  const data = await request.file();
  if (!data || data.fieldname !== 'file') {
    return reply.status(400).send({ error: 'Bad Request - Invalid input or missing file' });
  }

  const pdfPath = join(tmpdir(), `${randomUUID()}-${data.filename}`);
  const txtPath = `${pdfPath}.txt`;

  try {
    const buffer = await data.toBuffer();
    await writeFile(pdfPath, buffer);

    await new Promise((resolve, reject) => {
      execFile('pdftotext', [pdfPath, txtPath], (error) => {
        if (error) {
          reject(new Error('Internal Server Error - Conversion failed'));
        } else {
          resolve();
        }
      });
    });

    const textContent = await readFile(txtPath, 'utf8');
    reply.type('text/plain').send(textContent);
  } catch (error) {
    reply.status(500).send({ error: error.message });
  } finally {
    await unlink(pdfPath).catch(() => {});
    await unlink(txtPath).catch(() => {});
  }
});

server.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});