import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';

dotenv.config();

const app = fastify();
const PORT = 5000;

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      name TEXT PRIMARY KEY,
      data TEXT
    )
  `);
})();

// Add a new product to the catalog
app.post('/add', async (request, reply) => {
  const { name, ...properties } = request.body;

  if (!name || typeof name !== 'string') {
    return reply.status(400).send({ error: 'Invalid input: name is required and must be a string' });
  }

  const data = JSON.stringify(properties);

  try {
    await db.run('INSERT INTO products (name, data) VALUES (?, ?)', [name, data]);
    reply.status(201).send({ message: 'Product successfully added' });
  } catch (error) {
    if (error.code === 'SQLITE_CONSTRAINT') {
      reply.status(409).send({ error: 'Product with this name already exists' });
    } else {
      reply.status(500).send({ error: 'Internal server error' });
    }
  }
});

// Download the entire current catalog for a given product name
app.get('/download', async (request, reply) => {
  const { name } = request.query;

  if (!name || typeof name !== 'string') {
    return reply.status(400).send({ error: 'Invalid input: name is required and must be a string' });
  }

  try {
    const product = await db.get('SELECT data FROM products WHERE name = ?', [name]);

    if (product) {
      reply.status(200).send({ data: product.data });
    } else {
      reply.status(404).send({ error: 'Product not found' });
    }
  } catch (error) {
    reply.status(500).send({ error: 'Internal server error' });
  }
});

// Upload data for a product with the given name
app.post('/upload', async (request, reply) => {
  const { name, data } = request.body;

  if (!name || typeof name !== 'string' || !data) {
    return reply.status(400).send({ error: 'Invalid upload query: name and data are required' });
  }

  try {
    const result = await db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);
    if (result.changes === 0) {
      reply.status(404).send({ error: 'Product not found' });
    } else {
      reply.status(200).send({ message: 'The product with the given name was updated.' });
    }
  } catch (error) {
    reply.status(500).send({ error: 'Internal server error' });
  }
});

// Search for products in the catalog
app.get('/search', async (request, reply) => {
  const { query } = request.query;

  if (!query || typeof query !== 'string') {
    return reply.status(400).send({ error: 'Invalid search query: query is required and must be a string' });
  }

  try {
    const products = await db.all('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', [`%${query}%`, `%${query}%`]);

    const results = products.map(product => {
      try {
        return {
          name: product.name,
          ...JSON.parse(product.data)
        };
      } catch (error) {
        return { name: product.name, data: 'Invalid JSON data' };
      }
    });

    reply.status(200).send({ results });
  } catch (error) {
    reply.status(500).send({ error: 'Internal server error' });
  }
});

// Start the server
app.listen({ port: PORT, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});