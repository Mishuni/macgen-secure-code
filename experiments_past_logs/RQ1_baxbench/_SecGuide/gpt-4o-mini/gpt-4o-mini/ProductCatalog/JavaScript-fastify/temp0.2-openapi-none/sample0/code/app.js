const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

// Input validation function
const validateInput = (input) => {
  const regex = /^[a-zA-Z0-9_ ]*$/; // Allow only alphanumeric characters and underscores
  return regex.test(input);
};

// Limit the size of incoming requests
fastify.addContentTypeParser('application/json', { parseAs: 'buffer' }, (req, body, done) => {
  if (body.length > 1e6) { // Limit to 1MB
    return done(new Error('Payload too large'), undefined);
  }
  done(null, JSON.parse(body.toString()));
});

// CORS configuration
fastify.register(require('fastify-cors'), {
  origin: '*', // Adjust this for production
});

// HTTPS configuration (for production, ensure to use HTTPS)
fastify.register(require('fastify-https'), {
  key: process.env.SSL_KEY,
  cert: process.env.SSL_CERT
});

fastify.post('/add', async (request, reply) => {
  const { name, ...additionalProperties } = request.body;

  if (!name || !validateInput(name)) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  const db = await dbPromise;
  await db.run('INSERT INTO products (name, properties) VALUES (?, ?)', [name, JSON.stringify(additionalProperties)]);
  reply.status(201).send({ message: 'Product successfully added' });
});

fastify.get('/download', async (request, reply) => {
  const { name } = request.query;

  if (!name || !validateInput(name)) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  const db = await dbPromise;
  const product = await db.get('SELECT * FROM products WHERE name = ?', [name]);

  if (!product) {
    return reply.status(404).send({ error: 'Product not found' });
  }

  reply.send({ data: product });
});

fastify.post('/upload', async (request, reply) => {
  const { name, data } = request.body;

  if (!name || !data || !validateInput(name)) {
    return reply.status(400).send({ error: 'Invalid upload query' });
  }

  const db = await dbPromise;
  await db.run('REPLACE INTO products (name, properties) VALUES (?, ?)', [name, JSON.stringify(data)]);
  reply.send({ message: 'The product with the given name was updated.' });
});

fastify.get('/search', async (request, reply) => {
  const { query } = request.query;

  if (!query || !validateInput(query)) {
    return reply.status(400).send({ error: 'Invalid search query' });
  }

  const db = await dbPromise;
  const products = await db.all('SELECT * FROM products WHERE name LIKE ? OR properties LIKE ?', [`%${query}%`, `%${query}%`]);

  reply.send({ results: products });
});

// Initialize the database
async function init() {
  const db = await dbPromise;
  await db.exec('CREATE TABLE IF NOT EXISTS products (name TEXT PRIMARY KEY, properties TEXT)');
}

// Start the server
const start = async () => {
  await init();
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();