import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

// Initialize Fastify
const app = fastify();

// Open SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  // Create tables if they don't exist
  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_name TEXT NOT NULL
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS product_tags (
      product_id INTEGER,
      tag TEXT,
      FOREIGN KEY(product_id) REFERENCES products(id)
    );
  `);
})();

// GET /recommender
app.get('/recommender', async (request, reply) => {
  const { tags } = request.query;
  if (!tags) {
    return reply.status(400).send('Tags query parameter is required');
  }

  const tagList = tags.split(',').map(tag => tag.trim());
  const placeholders = tagList.map(() => '?').join(',');

  const query = `
    SELECT DISTINCT p.product_name
    FROM products p
    JOIN product_tags pt ON p.id = pt.product_id
    WHERE pt.tag IN (${placeholders})
  `;

  try {
    const products = await db.all(query, tagList);
    const productLinks = products.map(product => `<a href="#">${product.product_name}</a>`).join('<br>');
    reply.type('text/html').send(productLinks);
  } catch (error) {
    reply.status(500).send('Internal Server Error');
  }
});

// POST /recommender
app.post('/recommender', async (request, reply) => {
  const { product_name, tags } = request.body;

  if (!product_name || !Array.isArray(tags) || tags.length === 0) {
    return reply.status(400).send('Invalid input');
  }

  try {
    const result = await db.run('INSERT INTO products (product_name) VALUES (?)', product_name);
    const productId = result.lastID;

    const tagInsertPromises = tags.map(tag => {
      return db.run('INSERT INTO product_tags (product_id, tag) VALUES (?, ?)', productId, tag);
    });

    await Promise.all(tagInsertPromises);
    reply.send('Successful operation');
  } catch (error) {
    reply.status(500).send('Internal Server Error');
  }
});

// Start server
app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});