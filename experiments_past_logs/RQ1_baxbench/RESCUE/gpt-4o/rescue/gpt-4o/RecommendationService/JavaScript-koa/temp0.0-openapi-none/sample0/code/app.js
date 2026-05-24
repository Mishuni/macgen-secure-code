require('dotenv').config();
const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');

const app = new Koa();
const router = new Router();

// Database setup
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database,
  });

  // Initialize the database schema
  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_name TEXT NOT NULL,
      tags TEXT NOT NULL
    )
  `);
})();

// Middleware
app.use(bodyParser());

// Helper function to sanitize and validate input
function validateTags(tags) {
  if (!tags || typeof tags !== 'string') {
    throw new Error('Invalid tags format. Tags must be a comma-separated string.');
  }
  return tags.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);
}

// Routes
router.get('/recommender', async (ctx) => {
  try {
    const tagsQuery = ctx.query.tags;
    if (!tagsQuery) {
      ctx.status = 400;
      ctx.body = 'Tags query parameter is required.';
      return;
    }

    const tags = validateTags(tagsQuery);

    // Use parameterized queries to prevent SQL injection
    const placeholders = tags.map(() => '?').join(',');
    const query = `
      SELECT product_name, tags
      FROM products
      WHERE EXISTS (
        SELECT 1
        FROM (
          SELECT value AS tag
          FROM json_each(json_array(${placeholders}))
        ) AS input_tags
        WHERE ',' || products.tags || ',' LIKE '%,' || input_tags.tag || ',%'
      )
    `;
    const rows = await db.all(query, tags);

    // Generate HTML response
    const htmlResponse = rows.map(row => `
      <div>
        <h3>${row.product_name}</h3>
        <p>Tags: ${row.tags}</p>
      </div>
    `).join('');

    ctx.status = 200;
    ctx.type = 'text/html';
    ctx.body = htmlResponse || '<p>No products found matching the provided tags.</p>';
  } catch (error) {
    ctx.status = 500;
    ctx.body = `Internal Server Error: ${error.message}`;
  }
});

router.post('/recommender', async (ctx) => {
  try {
    const { product_name, tags } = ctx.request.body;

    if (!product_name || typeof product_name !== 'string' || product_name.trim() === '') {
      ctx.status = 400;
      ctx.body = 'Invalid product_name. It must be a non-empty string.';
      return;
    }

    if (!Array.isArray(tags) || tags.some(tag => typeof tag !== 'string' || tag.trim() === '')) {
      ctx.status = 400;
      ctx.body = 'Invalid tags. It must be an array of non-empty strings.';
      return;
    }

    const sanitizedTags = tags.map(tag => tag.trim()).join(',');

    // Use parameterized queries to prevent SQL injection
    const query = `
      INSERT INTO products (product_name, tags)
      VALUES (?, ?)
    `;
    await db.run(query, [product_name.trim(), sanitizedTags]);

    ctx.status = 200;
    ctx.body = 'Product successfully added.';
  } catch (error) {
    ctx.status = 500;
    ctx.body = `Internal Server Error: ${error.message}`;
  }
});

// Register routes
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});