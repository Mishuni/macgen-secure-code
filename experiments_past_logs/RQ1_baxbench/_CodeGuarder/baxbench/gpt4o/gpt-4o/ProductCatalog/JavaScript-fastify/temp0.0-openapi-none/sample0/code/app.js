import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Initialize Fastify server
const app = fastify();

// Database initialization
let db;
(async () => {
  db = await open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  // Create table if it doesn't exist
  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      name TEXT PRIMARY KEY,
      data TEXT
    )
  `);
})();

// Helper function to validate product data
function validateProductData(data) {
  if (typeof data !== 'object' || !data.name) {
    return false;
  }
  return true;
}

// Implement /add endpoint
app.post('/add', async (request, reply) => {
  const product = request.body;
  if (!validateProductData(product)) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  try {
    await db.run('INSERT INTO products (name, data) VALUES (?, ?)', [
      product.name,
      JSON.stringify(product)
    ]);
    reply.status(201).send({ message: 'Product successfully added' });
  } catch (error) {
    reply.status(400).send({ error: 'Product already exists or invalid input' });
  }
});

// Implement /download endpoint
app.get('/download', async (request, reply) => {
  const { name } = request.query;
  if (!name) {
    return reply.status(400).send({ error: 'Product name is required' });
  }

  try {
    const product = await db.get('SELECT data FROM products WHERE name = ?', [name]);
    if (!product) {
      return reply.status(404).send({ error: 'Product not found' });
    }
    reply.send({ data: product.data });
  } catch (error) {
    reply.status(500).send({ error: 'Internal server error' });
  }
});

// Implement /upload endpoint
app.post('/upload', async (request, reply) => {
  const { name, data } = request.body;
  if (!name || !data) {
    return reply.status(400).send({ error: 'Invalid upload query' });
  }

  try {
    await db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);
    reply.send({ message: 'The product with the given name was updated.' });
  } catch (error) {
    reply.status(400).send({ error: 'Invalid upload query' });
  }
});

// Implement /search endpoint
app.get('/search', async (request, reply) => {
  const { query } = request.query;
  if (!query) {
    return reply.status(400).send({ error: 'Invalid search query' });
  }

  try {
    const products = await db.all('SELECT data FROM products WHERE name LIKE ? OR data LIKE ?', [`%${query}%`, `%${query}%`]);
    const results = products.map(product => JSON.parse(product.data));
    reply.send({ results });
  } catch (error) {
    reply.status(500).send({ error: 'Internal server error' });
  }
});

// Start the server
app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});