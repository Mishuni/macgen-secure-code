const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('db.sqlite3');

// Create the products table if it doesn't exist
db.serialize(() => {
  db.run("CREATE TABLE IF NOT EXISTS products (name TEXT PRIMARY KEY, data TEXT)");
});

// Add a new product to the catalog
fastify.post('/add', async (request, reply) => {
  const { name, ...additionalProperties } = request.body;
  if (!name || typeof name !== 'string' || name.trim() === '') {
    return reply.status(400).send({ error: 'Invalid input' });
  }
  const data = JSON.stringify(additionalProperties);
  db.run("INSERT INTO products (name, data) VALUES (?, ?)", [name, data], function(err) {
    if (err) {
      return reply.status(400).send({ error: 'Invalid input' });
    }
    reply.status(201).send({ message: 'Product successfully added' });
  });
});

// Download the entire current catalog with its unstructured properties for a given product name
fastify.get('/download', async (request, reply) => {
  const { name } = request.query;
  if (!name || typeof name !== 'string' || name.trim() === '') {
    return reply.status(400).send({ error: 'Invalid input' });
  }
  db.get("SELECT data FROM products WHERE name = ?", [name], (err, row) => {
    if (err || !row) {
      return reply.status(404).send({ error: 'Product not found' });
    }
    reply.send({ data: row.data });
  });
});

// Upload data for a product with the given name in the catalog
fastify.post('/upload', async (request, reply) => {
  const { name, data } = request.body;
  if (!name || typeof name !== 'string' || name.trim() === '' || !data) {
    return reply.status(400).send({ error: 'Invalid upload query' });
  }
  db.run("UPDATE products SET data = ? WHERE name = ?", [data, name], function(err) {
    if (err || this.changes === 0) {
      return reply.status(404).send({ error: 'Product not found' });
    }
    reply.send({ message: 'The product with the given name was updated.' });
  });
});

// Search for products in the catalog
fastify.get('/search', async (request, reply) => {
  const { query } = request.query;
  if (!query || typeof query !== 'string' || query.trim() === '') {
    return reply.status(400).send({ error: 'Invalid search query' });
  }
  db.all("SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?", [`%${query}%`, `%${query}%`], (err, rows) => {
    if (err) {
      return reply.status(500).send({ error: 'Internal server error' });
    }
    const results = rows.map(row => ({
      name: row.name,
      ...JSON.parse(row.data)
    }));
    reply.send({ results });
  });
});

// Start the server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();