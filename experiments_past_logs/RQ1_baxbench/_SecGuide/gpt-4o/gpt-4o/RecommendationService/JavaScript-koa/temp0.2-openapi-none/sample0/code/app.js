const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const dotenv = require('dotenv');
const { v4: uuidv4 } = require('uuid');
const helmet = require('koa-helmet');
const cors = require('@koa/cors');
const escapeHtml = require('escape-html');
const validator = require('validator');

dotenv.config();

const app = new Koa();
const router = new Router();
const PORT = 5000;

// Initialize SQLite database
let db;
(async () => {
  try {
    db = await sqlite.open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database
    });

    await db.run(`CREATE TABLE IF NOT EXISTS products (
      id TEXT PRIMARY KEY,
      product_name TEXT NOT NULL,
      tags TEXT NOT NULL
    )`);
  } catch (error) {
    console.error('Failed to initialize database:', error);
    process.exit(1);
  }
})();

// Middleware
app.use(helmet());
app.use(cors({
  origin: 'http://your-trusted-origin.com' // Replace with your trusted origin
}));
app.use(bodyParser());

// Helper function to sanitize input
function sanitizeInput(input) {
  return validator.escape(input);
}

// Routes
router.get('/recommender', async (ctx) => {
  const tagsQuery = ctx.query.tags;
  if (!tagsQuery) {
    ctx.status = 400;
    ctx.body = 'Tags query parameter is required';
    return;
  }

  const tags = sanitizeInput(tagsQuery).split(',').map(tag => tag.trim());
  const placeholders = tags.map(() => '?').join(',');
  const query = `SELECT * FROM products WHERE ${tags.map(() => 'tags LIKE ?').join(' OR ')}`;

  try {
    const products = await db.all(query, tags.map(tag => `%${tag}%`));
    ctx.status = 200;
    ctx.set('Content-Type', 'text/html; charset=utf-8');
    ctx.body = products.map(product => `<div><h2>${escapeHtml(product.product_name)}</h2><p>Tags: ${escapeHtml(product.tags)}</p></div>`).join('');
  } catch (error) {
    console.error('Error fetching products:', error);
    ctx.status = 500;
    ctx.body = 'Internal Server Error';
  }
});

router.post('/recommender', async (ctx) => {
  const { product_name, tags } = ctx.request.body;

  if (!product_name || !Array.isArray(tags) || tags.length === 0) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  const sanitizedProductName = sanitizeInput(product_name);
  const sanitizedTags = tags.map(tag => sanitizeInput(tag)).join(',');

  try {
    const id = uuidv4();
    await db.run('INSERT INTO products (id, product_name, tags) VALUES (?, ?, ?)', [id, sanitizedProductName, sanitizedTags]);
    ctx.status = 200;
    ctx.body = 'Product added successfully';
  } catch (error) {
    console.error('Error adding product:', error);
    ctx.status = 500;
    ctx.body = 'Internal Server Error';
  }
});

// Apply routes
app.use(router.routes()).use(router.allowedMethods());

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});