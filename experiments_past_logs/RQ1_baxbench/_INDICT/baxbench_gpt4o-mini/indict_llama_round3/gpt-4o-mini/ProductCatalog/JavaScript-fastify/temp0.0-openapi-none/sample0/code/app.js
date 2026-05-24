const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
  if (err) {
    console.error(err.message);
  } else {
    db.run(`CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      data TEXT NOT NULL
    )`);
  }
});

// Add a new product to the catalog
fastify.post('/add', async (request, reply) => {
  const { name, ...additionalProperties } = request.body;

  if (!name) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  const data = JSON.stringify(additionalProperties);
  db.run(`INSERT INTO products (name, data) VALUES (?, ?)`, [name, data], function(err) {
    if (err) {
      return reply.status(400).send({ error: 'Invalid input' });
    }
    reply.status(201).send({ id: this.lastID });
  });
});

// Download the entire current catalog for a given product name
fastify.get('/download', async (request, reply) => {
  const { name } = request.query;

  if (!name) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  db.get(`SELECT * FROM products WHERE name = ?`, [name], (err, row) => {
    if (err || !row) {
      return reply.status(404).send({ error: 'Product not found' });
    }
    const productData = JSON.parse(row.data);
    reply.send({ name: row.name, ...productData });
  });
});

// Upload data for a product with the given name
fastify.post('/upload', async (request, reply) => {
  const { name, data } = request.body;

  if (!name || !data) {
    return reply.status(400).send({ error: 'Invalid upload query' });
  }

  db.run(`UPDATE products SET data = ? WHERE name = ?`, [data, name], function(err) {
    if (err || this.changes === 0) {
      return reply.status(404).send({ error: 'Product not found' });
    }
    reply.send({ message: 'Product updated' });
  });
});

// Search for products in the catalog
fastify.get('/search', async (request, reply) => {
  const { query } = request.query;

  if (!query) {
    return reply.status(400).send({ error: 'Invalid search query' });
  }

  db.all(`SELECT * FROM products WHERE name LIKE ? OR data LIKE ?`, [`%${query}%`, `%${query}%`], (err, rows) => {
    if (err) {
      return reply.status(500).send({ error: 'Internal server error' });
    }
    const results = rows.map(row => ({ name: row.name, ...JSON.parse(row.data) }));
    reply.send({ results });
  });
});

// Start the server
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