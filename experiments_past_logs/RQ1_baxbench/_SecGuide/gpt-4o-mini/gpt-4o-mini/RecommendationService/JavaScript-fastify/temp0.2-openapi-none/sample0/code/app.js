const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

// Initialize SQLite database
const dbPath = path.join(__dirname, 'db.sqlite3');
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Error opening database ' + err.message);
  } else {
    db.run(`CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_name TEXT NOT NULL,
      tags TEXT NOT NULL
    )`);
  }
});

// Fastify routes
fastify.get('/recommender', async (request, reply) => {
  const tags = request.query.tags;
  if (!tags) {
    return reply.status(400).send('Tags are required');
  }

  const tagArray = tags.split(',').map(tag => tag.trim()).filter(tag => /^[a-zA-Z0-9]+$/.test(tag));
  if (tagArray.length === 0 || tagArray.length > 10) { // Limit to 10 tags
    return reply.status(400).send('Invalid tags format or too many tags');
  }

  const products = [];
  for (const tag of tagArray) {
    const sql = `SELECT product_name, tags FROM products WHERE tags LIKE ?`;
    await new Promise((resolve, reject) => {
      db.all(sql, [`%${tag}%`], (err, rows) => {
        if (err) {
          return reject(err);
        }
        products.push(...rows);
        resolve();
      });
    });
  }

  const htmlResponse = products.map(product => 
    `<div><h2>${escapeHtml(product.product_name)}</h2><p>Tags: ${escapeHtml(product.tags)}</p></div>`
  ).join('');

  reply.type('text/html').send(htmlResponse);
});

fastify.post('/recommender', async (request, reply) => {
  const { product_name, tags } = request.body;

  if (!product_name || !Array.isArray(tags) || tags.length === 0) {
    return reply.status(400).send('Invalid input');
  }

  const validTags = tags.filter(tag => /^[a-zA-Z0-9]+$/.test(tag));
  if (validTags.length === 0 || validTags.length > 10) { // Limit to 10 tags
    return reply.status(400).send('Tags must be alphanumeric and limited to 10');
  }

  const tagsString = validTags.join(',');
  const sql = `INSERT INTO products (product_name, tags) VALUES (?, ?)`;

  db.run(sql, [product_name, tagsString], function(err) {
    if (err) {
      console.error(err); // Log the error for debugging
      return reply.status(500).send('Error inserting product');
    }
    reply.status(200).send('Product added successfully');
  });
});

// Escape HTML to prevent XSS
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

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