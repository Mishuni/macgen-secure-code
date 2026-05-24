const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const DB_PATH = process.env.DB_PATH || 'db.sqlite3';

async function initDb() {
  const db = await open({
    filename: DB_PATH,
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_name TEXT NOT NULL,
      tags TEXT NOT NULL
    )
  `);

  return db;
}

const dbPromise = initDb();

fastify.get('/recommender', async (request, reply) => {
  const { tags } = request.query;

  if (!tags) {
    return reply.status(400).send('Tags are required');
  }

  const tagList = tags.split(',').map(tag => tag.trim());
  const placeholders = tagList.map(() => '?').join(',');
  const sql = `SELECT product_name, tags FROM products WHERE tags IN (${placeholders})`;
  
  const db = await dbPromise;
  const products = await db.all(sql, tagList);

  const htmlResponse = products.map(product => `<div><h2>${product.product_name}</h2><p>Tags: ${product.tags}</p></div>`).join('');
  reply.type('text/html').send(htmlResponse);
});

fastify.post('/recommender', async (request, reply) => {
  const { product_name, tags } = request.body;

  if (!product_name || typeof product_name !== 'string' || product_name.trim() === '' || !Array.isArray(tags)) {
    return reply.status(400).send('Invalid input');
  }

  const tagString = tags.join(',');
  const sql = `INSERT INTO products (product_name, tags) VALUES (?, ?)`;
  
  const db = await dbPromise;
  await db.run(sql, [product_name, tagString]);

  reply.status(200).send('Product added successfully');
});

const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server is running on http://0.0.0.0:5000');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();