import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';

dotenv.config();

const app = fastify();
const PORT = 5000;
const DB_FILE = 'db.sqlite3';

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: DB_FILE,
    driver: sqlite3.Database,
  });

  // Create the products table if it doesn't exist
  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      data TEXT NOT NULL
    )
  `);
})();

// Helper function to validate product name
function validateProductName(name) {
  return typeof name === 'string' && name.trim().length > 0;
}

// Helper function to validate product data
function validateProductData(data) {
  return typeof data === 'string' && data.trim().length > 0;
}

// Route: Add a new product to the catalog
app.post('/add', async (request, reply) => {
  const { name, ...properties } = request.body;

  if (!validateProductName(name)) {
    return reply.status(400).send({ error: 'Invalid product name' });
  }

  const data = JSON.stringify(properties);

  try {
    await db.run('INSERT INTO products (name, data) VALUES (?, ?)', [name, data]);
    return reply.status(201).send({ message: 'Product successfully added' });
  } catch (err) {
    if (err.code === 'SQLITE_CONSTRAINT') {
      return reply.status(400).send({ error: 'Product with this name already exists' });
    }
    return reply.status(500).send({ error: 'Internal server error' });
  }
});

// Route: Download the catalog for a given product name
app.get('/download', async (request, reply) => {
  const { name } = request.query;

  if (!validateProductName(name)) {
    return reply.status(400).send({ error: 'Invalid product name' });
  }

  try {
    const product = await db.get('SELECT data FROM products WHERE name = ?', [name]);
    if (!product) {
      return reply.status(404).send({ error: 'Product not found' });
    }
    return reply.status(200).send({ data: product.data });
  } catch (err) {
    return reply.status(500).send({ error: 'Internal server error' });
  }
});

// Route: Upload data for a product
app.post('/upload', async (request, reply) => {
  const { name, data } = request.body;

  if (!validateProductName(name) || !validateProductData(data)) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  try {
    const result = await db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);
    if (result.changes === 0) {
      return reply.status(404).send({ error: 'Product not found' });
    }
    return reply.status(200).send({ message: 'Product successfully updated' });
  } catch (err) {
    return reply.status(500).send({ error: 'Internal server error' });
  }
});

// Route: Search for products in the catalog
app.get('/search', async (request, reply) => {
  const { query } = request.query;

  if (!query || typeof query !== 'string' || query.trim().length === 0) {
    return reply.status(400).send({ error: 'Invalid search query' });
  }

  try {
    const products = await db.all('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', [`%${query}%`, `%${query}%`]);
    const results = products.map((product) => ({
      name: product.name,
      ...JSON.parse(product.data),
    }));
    return reply.status(200).send({ results });
  } catch (err) {
    return reply.status(500).send({ error: 'Internal server error' });
  }
});

// Start the server
app.listen({ port: PORT, host: '0.0.0.0' }, (err) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server running at http://0.0.0.0:${PORT}`);
});