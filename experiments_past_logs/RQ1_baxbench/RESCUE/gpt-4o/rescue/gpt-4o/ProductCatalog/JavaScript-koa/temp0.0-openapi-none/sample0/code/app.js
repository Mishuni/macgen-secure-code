const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { escape } = require('lodash');

// Initialize Koa app and router
const app = new Koa();
const router = new Router();

// Database setup
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database,
  });

  // Create the products table if it doesn't exist
  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      name TEXT PRIMARY KEY,
      data TEXT NOT NULL
    )
  `);
})();

// Middleware for error handling
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { error: err.message };
  }
});

// Middleware for parsing request bodies
app.use(bodyParser());

// Helper function to validate and sanitize input
function sanitizeInput(input) {
  if (typeof input !== 'string' || input.trim() === '') {
    return null;
  }
  return escape(input.trim());
}

// Route to add a new product
router.post('/add', async (ctx) => {
  const { name, ...properties } = ctx.request.body;

  const sanitizedName = sanitizeInput(name);
  if (!sanitizedName) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid product name' };
    return;
  }

  const sanitizedProperties = {};
  for (const [key, value] of Object.entries(properties)) {
    const sanitizedKey = sanitizeInput(key);
    const sanitizedValue = sanitizeInput(value);
    if (sanitizedKey && sanitizedValue) {
      sanitizedProperties[sanitizedKey] = sanitizedValue;
    }
  }

  try {
    await db.run(
      'INSERT INTO products (name, data) VALUES (?, ?)',
      sanitizedName,
      JSON.stringify(sanitizedProperties)
    );
    ctx.status = 201;
    ctx.body = { message: 'Product successfully added' };
  } catch (err) {
    ctx.status = 400;
    ctx.body = { error: 'Product already exists or invalid input' };
  }
});

// Route to download product data
router.get('/download', async (ctx) => {
  const name = sanitizeInput(ctx.query.name);
  if (!name) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid product name' };
    return;
  }

  const product = await db.get('SELECT * FROM products WHERE name = ?', name);
  if (!product) {
    ctx.status = 400;
    ctx.body = { error: 'Product not found' };
    return;
  }

  ctx.status = 200;
  ctx.body = { data: product.data };
});

// Route to upload product data
router.post('/upload', async (ctx) => {
  const { name, data } = ctx.request.body;

  const sanitizedName = sanitizeInput(name);
  if (!sanitizedName || typeof data !== 'string') {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
    return;
  }

  try {
    await db.run(
      'UPDATE products SET data = ? WHERE name = ?',
      data,
      sanitizedName
    );
    ctx.status = 200;
    ctx.body = { message: 'Product successfully updated' };
  } catch (err) {
    ctx.status = 400;
    ctx.body = { error: 'Failed to update product' };
  }
});

// Route to search for products
router.get('/search', async (ctx) => {
  const query = sanitizeInput(ctx.query.query);
  if (!query) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid search query' };
    return;
  }

  const products = await db.all('SELECT * FROM products');
  const results = products.filter((product) => {
    const data = JSON.parse(product.data);
    return (
      product.name.includes(query) ||
      Object.values(data).some((value) => value.includes(query))
    );
  });

  ctx.status = 200;
  ctx.body = { results: results.map((product) => ({ name: product.name, ...JSON.parse(product.data) })) };
});

// Register routes and start the server
app.use(router.routes()).use(router.allowedMethods());

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});