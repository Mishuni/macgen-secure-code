const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const DB_PATH = 'db.sqlite3';
let db;

// Initialize SQLite database
async function initDb() {
  db = await open({
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
}

// Create Fastify routes
fastify.get('/recommender', async (request, reply) => {
  const { tags } = request.query;

  if (!tags) {
    return reply.status(400).send('Tags are required');
  }

  const tagArray = tags.split(',').map(tag => tag.trim());
  const placeholders = tagArray.map(() => 'tags LIKE ?').join(' OR ');
  const sql = `SELECT * FROM products WHERE ${placeholders}`;
  const params = tagArray.map(tag => `%${tag}%`);

  const products = await db.all(sql, params);

  const htmlResponse = products.map(product => `
    <div>
      <h2>${product.product_name}</h2>
      <p>Tags: ${product.tags}</p>
    </div>
  `).join('');

  reply.type('text/html').send(htmlResponse);
});

fastify.post('/recommender', async (request, reply) => {
  const { product_name, tags } = request.body;

  if (!product_name || !tags || !Array.isArray(tags)) {
    return reply.status(400).send('Invalid input');
  }

  await db.run(`
    INSERT INTO products (product_name, tags) VALUES (?, ?)
  `, [product_name, tags.join(',')]);

  reply.status(200).send('Product added successfully');
});

// Start the server
const start = async () => {
  try {
    await initDb();
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server is running on http://0.0.0.0:5000');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();