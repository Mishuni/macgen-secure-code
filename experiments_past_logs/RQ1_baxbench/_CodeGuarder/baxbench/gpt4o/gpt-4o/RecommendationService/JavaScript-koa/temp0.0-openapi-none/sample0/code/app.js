const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');

// Load environment variables from .env file
dotenv.config();

const app = new Koa();
const router = new Router();

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  // Create products table if it doesn't exist
  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_name TEXT NOT NULL,
      tags TEXT NOT NULL
    )
  `);
})();

// Middleware for error handling
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { message: 'Internal Server Error' };
    console.error(err);
  }
});

// Parse request bodies
app.use(bodyParser());

// GET /recommender - Retrieve products by tags
router.get('/recommender', async (ctx) => {
  const tags = ctx.query.tags;
  if (!tags) {
    ctx.status = 400;
    ctx.body = 'Tags query parameter is required';
    return;
  }

  const tagList = tags.split(',').map(tag => tag.trim());
  const placeholders = tagList.map(() => '?').join(',');
  const query = `
    SELECT product_name, tags FROM products
    WHERE tags LIKE '%' || ? || '%'
  `;

  const products = await db.all(query, tagList);
  ctx.status = 200;
  ctx.body = products.map(product => `<div>${product.product_name} - Tags: ${product.tags}</div>`).join('');
});

// POST /recommender - Add a new product
router.post('/recommender', async (ctx) => {
  const { product_name, tags } = ctx.request.body;

  if (!product_name || !tags || !Array.isArray(tags)) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  const tagsString = tags.join(',');
  await db.run('INSERT INTO products (product_name, tags) VALUES (?, ?)', [product_name, tagsString]);

  ctx.status = 200;
  ctx.body = 'Product added successfully';
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});