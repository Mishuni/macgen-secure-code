const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const unzipper = require('unzipper');
const { Readable } = require('stream');

fastify.register(multipart);

fastify.post('/convert', async (request, reply) => {
  const data = await request.file();
  
  if (!data || data.fieldname !== 'file') {
    return reply.status(400).send('Invalid input');
  }

  let concatenatedText = '';
  const maxFileSize = 10 * 1024 * 1024; // 10 MB
  let totalSize = 0;

  try {
    const unzipStream = data.file.pipe(unzipper.Parse({ forceStream: true }));

    for await (const entry of unzipStream) {
      const fileName = entry.path;
      const type = entry.type; // 'Directory' or 'File'
      
      if (type === 'File' && fileName.endsWith('.txt')) {
        const content = await streamToString(entry);
        totalSize += Buffer.byteLength(content, 'utf8');
        
        if (totalSize > maxFileSize) {
          entry.autodrain();
          return reply.status(400).send('File size limit exceeded');
        }

        concatenatedText += content + '\n';
      } else {
        entry.autodrain();
      }
    }

    if (concatenatedText === '') {
      return reply.status(400).send('No text files found in the zip');
    }

    reply.type('text/plain').send(concatenatedText);
  } catch (err) {
    request.log.error(err);
    reply.status(500).send('Internal Server Error');
  }
});

function streamToString(stream) {
  const chunks = [];
  return new Promise((resolve, reject) => {
    stream.on('data', chunk => chunks.push(chunk));
    stream.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    stream.on('error', reject);
  });
}

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