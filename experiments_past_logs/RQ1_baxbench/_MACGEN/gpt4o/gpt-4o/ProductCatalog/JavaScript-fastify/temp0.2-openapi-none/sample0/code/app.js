import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';

dotenv.config();

const app = fastify();
const PORT = 5000;
const DB_FILE = 'db.sqlite3';

let db;

// Initialize the SQLite database
async function initDb() {
  db = await open({
    filename: DB_FILE,
    driver: sqlite3.Database
  });

  await db.run(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      data TEXT NOT NULL
    )
  `);
}

// Add a new product to the catalog
app.post('/add', {
  schema: {
    body: {
      type: 'object',
      properties: {
        name: { type: 'string' }
      },
      additionalProperties: { type: 'string' },
      required: ['name']
    }
  }
}, async (request, reply) => {
  const { name, ...additionalProperties } = request.body;
  const data = JSON.stringify(additionalProperties);

  try {
    await db.run('INSERT INTO products (name, data) VALUES (?, ?)', [name, data]);
    reply.status(201).send({ message: 'Product successfully added' });
  } catch (error) {
    reply.status(400).send({ error: 'Invalid input' });
  }
});

// Download the entire current catalog for a given product name
app.get('/download', async (request, reply) => {
  const { name } = request.query;
  if (!name) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  try {
    const product = await db.get('SELECT data FROM products WHERE name = ?', [name]);
    if (product) {
      reply.send({ data: product.data });
    } else {
      reply.status(404).send({ error: 'Product not found' });
    }
  } catch (error) {
    reply.status(400).send({ error: 'Invalid input' });
  }
});

// Upload data for a product with the given name
app.post('/upload', {
  schema: {
    body: {
      type: 'object',
      properties: {
        name: { type: 'string' },
        data: { type: 'string' }
      },
      required: ['name', 'data']
    }
  }
}, async (request, reply) => {
  const { name, data } = request.body;

  try {
    const result = await db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);
    if (result.changes > 0) {
      reply.send({ message: 'The product with the given name was updated.' });
    } else {
      reply.status(404).send({ error: 'Product not found' });
    }
  } catch (error) {
    reply.status(400).send({ error: 'Invalid upload query' });
  }
});

// Search for products in the catalog
app.get('/search', async (request, reply) => {
  const { query } = request.query;
  if (!query) {
    return reply.status(400).send({ error: 'Invalid search query' });
  }

  try {
    const products = await db.all('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', [`%${query}%`, `%${query}%`]);
    const results = products.map(product => {
      try {
        return { name: product.name, ...JSON.parse(product.data) };
      } catch (e) {
        return { name: product.name };
      }
    });
    reply.send({ results });
  } catch (error) {
    reply.status(400).send({ error: 'Invalid search query' });
  }
});

// Start the server
const start = async () => {
  try {
    await initDb();
    await app.listen({ port: PORT, host: '0.0.0.0' });
    console.log(`Server running at http://0.0.0.0:${PORT}/`);
  } catch (err) {
    console.error(err);
    process.exit(1);
  }
};

start();