const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

// Initialize the database
async function initDb() {
  const db = await dbPromise;
  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      data TEXT NOT NULL
    )
  `);
}

// Add a new product to the catalog
fastify.post('/add', async (request, reply) => {
  const { name, ...additionalProperties } = request.body;

  if (!name) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  const db = await dbPromise;
  const data = JSON.stringify(additionalProperties);

  try {
    await db.run('INSERT INTO products (name, data) VALUES (?, ?)', [name, data]);
    reply.status(201).send({ message: 'Product successfully added' });
  } catch (error) {
    if (error.code === 'SQLITE_CONSTRAINT') {
      return reply.status(400).send({ error: 'Product already exists' });
    }
    reply.status(500).send({ error: 'Database error' });
  }
});

// Download the entire current catalog for a given product name
fastify.get('/download', async (request, reply) => {
  const { name } = request.query;

  if (!name) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  const db = await dbPromise;
  const product = await db.get('SELECT data FROM products WHERE name = ?', [name]);

  if (!product) {
    return reply.status(404).send({ error: 'Product not found' });
  }

  reply.send({ data: product.data });
});

// Upload data for a product with the given name
fastify.post('/upload', async (request, reply) => {
  const { name, data } = request.body;

  if (!name || !data) {
    return reply.status(400).send({ error: 'Invalid upload query' });
  }

  const db = await dbPromise;

  try {
    await db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);
    reply.send({ message: 'Product updated successfully' });
  } catch (error) {
    reply.status(500).send({ error: 'Database error' });
  }
});

// Search for products in the catalog
fastify.get('/search', async (request, reply) => {
  const { query } = request.query;

  if (!query) {
    return reply.status(400).send({ error: 'Invalid search query' });
  }

  const db = await dbPromise;
  const products = await db.all('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', [`%${query}%`, `%${query}%`]);

  reply.send({ results: products.map(product => ({ name: product.name, ...JSON.parse(product.data) })) });
});

// Start the server
const start = async () => {
  await initDb();
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();