import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';
import { escape } from 'html-escaper';

dotenv.config();

const app = fastify();
const PORT = 5000;
const HOST = '0.0.0.0'; // Allow external access for production

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_name TEXT NOT NULL,
      tags TEXT NOT NULL
    )
  `);
})();

// GET /recommender
app.get('/recommender', async (request, reply) => {
  const { tags } = request.query;
  if (!tags) {
    return reply.status(400).send('Tags query parameter is required.');
  }

  const tagList = tags.split(',').map(tag => tag.trim());

  const placeholders = tagList.map(() => 'tags LIKE ?').join(' OR ');
  const query = `SELECT product_name, tags FROM products WHERE ${placeholders}`;

  try {
    const products = await db.all(query, tagList.map(tag => `%${tag}%`));
    const productLinks = products.map(product => {
      const encodedProductName = escape(product.product_name);
      return `<a href="/product/${encodedProductName}">${encodedProductName}</a>`;
    }).join('<br>');

    reply.type('text/html').send(productLinks);
  } catch (error) {
    console.error('Error fetching products:', error.message); // Log error message
    reply.status(500).send('Internal Server Error');
  }
});

// POST /recommender
app.post('/recommender', async (request, reply) => {
  const { product_name, tags } = request.body;

  if (!product_name || !tags || !Array.isArray(tags)) {
    return reply.status(400).send('Invalid input');
  }

  const sanitizedProductName = product_name.trim();
  const sanitizedTags = tags.map(tag => tag.trim()).filter(tag => tag.length > 0).join(',');

  try {
    await db.run('INSERT INTO products (product_name, tags) VALUES (?, ?)', [sanitizedProductName, sanitizedTags]);
    reply.status(200).send('Product added successfully');
  } catch (error) {
    console.error('Error adding product:', error.message); // Log error message
    reply.status(500).send('Internal Server Error');
  }
});

// Start the server
app.listen({ port: PORT, host: HOST }, (err, address) => {
  if (err) {
    console.error('Error starting server:', err.message);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});