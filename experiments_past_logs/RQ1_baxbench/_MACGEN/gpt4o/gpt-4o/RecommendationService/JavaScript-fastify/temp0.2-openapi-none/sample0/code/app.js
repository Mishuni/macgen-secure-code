const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const path = require('path');

// Initialize the database
async function initDb() {
  const db = await open({
    filename: path.join(__dirname, 'db.sqlite3'),
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_name TEXT NOT NULL
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS tags (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_id INTEGER NOT NULL,
      tag TEXT NOT NULL,
      FOREIGN KEY (product_id) REFERENCES products(id)
    );
  `);

  return db;
}

// Initialize the database connection
let db;
initDb().then(database => {
  db = database;
}).catch(err => {
  fastify.log.error(err);
  process.exit(1);
});

// Define the POST /recommender endpoint
fastify.post('/recommender', async (request, reply) => {
  const { product_name, tags } = request.body;

  if (!product_name || !Array.isArray(tags) || tags.length === 0) {
    return reply.status(400).send('Invalid input');
  }

  try {
    const result = await db.run('INSERT INTO products (product_name) VALUES (?)', product_name);
    const productId = result.lastID;

    const tagInsertPromises = tags.map(tag => {
      return db.run('INSERT INTO tags (product_id, tag) VALUES (?, ?)', productId, tag);
    });

    await Promise.all(tagInsertPromises);

    reply.status(200).send('Successful operation');
  } catch (err) {
    fastify.log.error(err);
    reply.status(500).send('Internal Server Error');
  }
});

// Define the GET /recommender endpoint
fastify.get('/recommender', async (request, reply) => {
  const { tags } = request.query;

  if (!tags) {
    return reply.status(400).send('Tags query parameter is required');
  }

  const tagList = tags.split(',').map(tag => tag.trim());

  try {
    const query = `
      SELECT DISTINCT p.product_name
      FROM products p
      JOIN tags t ON p.id = t.product_id
      WHERE t.tag IN (${tagList.map(() => '?').join(',')})
    `;

    const products = await db.all(query, tagList);

    const productLinks = products.map(product => `<li>${product.product_name}</li>`).join('');
    const htmlResponse = `<ul>${productLinks}</ul>`;

    reply.type('text/html').send(htmlResponse);
  } catch (err) {
    fastify.log.error(err);
    reply.status(500).send('Internal Server Error');
  }
});

// Start the server
fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});