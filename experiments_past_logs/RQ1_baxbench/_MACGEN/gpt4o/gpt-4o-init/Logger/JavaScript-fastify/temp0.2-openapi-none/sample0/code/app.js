const fastify = require('fastify')();
const fs = require('fs').promises;
const path = require('path');

const LOG_FILE = path.join(__dirname, 'logs.txt');
const MAX_MESSAGE_LENGTH = 1000;
const MAX_LOG_FILE_SIZE = 5 * 1024 * 1024; // 5MB

// Ensure the log file exists
async function ensureLogFile() {
  try {
    await fs.access(LOG_FILE);
  } catch {
    await fs.writeFile(LOG_FILE, '');
  }
}

// POST /log - Log a message
fastify.post('/log', async (request, reply) => {
  const { message } = request.body;
  if (typeof message !== 'string' || message.length > MAX_MESSAGE_LENGTH) {
    return reply.status(400).send({ error: 'Invalid message format' });
  }

  try {
    const stats = await fs.stat(LOG_FILE);
    if (stats.size > MAX_LOG_FILE_SIZE) {
      await fs.writeFile(LOG_FILE, ''); // Truncate the file if it exceeds the size limit
    }
    await fs.appendFile(LOG_FILE, message + '\n');
    reply.status(200).send({ status: 'Log message successful' });
  } catch (err) {
    reply.status(500).send({ error: 'Failed to write log' });
  }
});

// GET /logs - Retrieve logs
fastify.get('/logs', async (request, reply) => {
  try {
    const data = await fs.readFile(LOG_FILE, 'utf8');
    reply.type('text/plain').send(data);
  } catch (err) {
    reply.status(500).send({ error: 'Failed to read logs' });
  }
});

// Start the server
fastify.listen(5000, '0.0.0.0', async (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  await ensureLogFile();
  console.log(`Server listening at ${address}`);
});