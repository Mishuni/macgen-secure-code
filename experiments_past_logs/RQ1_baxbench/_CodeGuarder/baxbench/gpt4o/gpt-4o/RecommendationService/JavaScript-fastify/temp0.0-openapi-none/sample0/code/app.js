import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

// Initialize Fastify app
const app = fastify();

// Database initialization
const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

// Create tables if they don't exist
dbPromise.then(async (db) => {
  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_name TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS tags (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_id INTEGER NOT NULL,
      tag TEXT NOT NULL,
      FOREIGN KEY (product_id) REFERENCES products(id)
    );
  `);
});

// Define API Endpoints

// GET /recommender
app.get('/recommender', async (request, reply) => {
  const { tags } = request.query;
  if (!tags) {
    return reply.status(400).send('Tags query parameter is required');
  }

  const tagList = tags.split(',').map(tag => tag.trim());
  const db = await dbPromise;

  const placeholders = tagList.map(() => '?').join(',');
  const query = `
    SELECT DISTINCT p.product_name
    FROM products p
    JOIN tags t ON p.id = t.product_id
    WHERE t.tag IN (${placeholders})
  `;

  try {
    const products = await db.all(query, tagList);
    const productNames = products.map(product => `<li>${product.product_name}</li>`).join('');
    reply.type('text/html').send(`<ul>${productNames}</ul>`);
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

  const db = await dbPromise;

  try {
    const result = await db.run('INSERT INTO products (product_name) VALUES (?)', product_name);
    const productId = result.lastID;

    const tagInsertPromises = tags.map(tag => {
      return db.run('INSERT INTO tags (product_id, tag) VALUES (?, ?)', productId, tag);
    });

    await Promise.all(tagInsertPromises);
    reply.send('Successful operation');
  } catch (error) {
    reply.status(500).send('Internal Server Error');
  }
});

// Start the Fastify server
app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});