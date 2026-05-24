const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const validator = require('validator');

dotenv.config();

const app = new Koa();
const router = new Router();

let db;

// Initialize the SQLite database
async function initDb() {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  await db.run(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL,
      data TEXT NOT NULL
    )
  `);
}

// Middleware to handle errors
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { error: 'An unexpected error occurred' };
    console.error('Error:', err.message); // Log only the error message
  }
});

// Parse request bodies
app.use(bodyParser());

// Validate and sanitize input
function validateAndSanitizeInput(input) {
  if (typeof input !== 'string' || input.trim() === '') {
    return false;
  }
  return validator.escape(input.trim());
}

// Add a new product
router.post('/add', async (ctx) => {
  const { name, ...additionalProperties } = ctx.request.body;

  const sanitizedName = validateAndSanitizeInput(name);
  if (!sanitizedName) {
    ctx.status = 400;
    ctx.body = { error: 'Product name is required and must be a non-empty string' };
    return;
  }

  const data = JSON.stringify(additionalProperties);

  try {
    await db.run('INSERT INTO products (name, data) VALUES (?, ?)', [sanitizedName, data]);
    ctx.status = 201;
    ctx.body = { message: 'Product successfully added' };
  } catch (err) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input or product already exists' };
  }
});

// Download product data
router.get('/download', async (ctx) => {
  const { name } = ctx.query;

  const sanitizedName = validateAndSanitizeInput(name);
  if (!sanitizedName) {
    ctx.status = 400;
    ctx.body = { error: 'Product name is required and must be a non-empty string' };
    return;
  }

  const product = await db.get('SELECT data FROM products WHERE name = ?', [sanitizedName]);

  if (product) {
    ctx.status = 200;
    ctx.body = { data: product.data };
  } else {
    ctx.status = 404;
    ctx.body = { error: 'Product not found' };
  }
});

// Upload product data
router.post('/upload', async (ctx) => {
  const { name, data } = ctx.request.body;

  const sanitizedName = validateAndSanitizeInput(name);
  const sanitizedData = validateAndSanitizeInput(data);
  if (!sanitizedName || !sanitizedData) {
    ctx.status = 400;
    ctx.body = { error: 'Product name and data are required and must be non-empty strings' };
    return;
  }

  try {
    const result = await db.run('UPDATE products SET data = ? WHERE name = ?', [sanitizedData, sanitizedName]);

    if (result.changes === 0) {
      ctx.status = 404;
      ctx.body = { error: 'Product not found' };
    } else {
      ctx.status = 200;
      ctx.body = { message: 'Product successfully updated' };
    }
  } catch (err) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid upload query' };
  }
});

// Search for products
router.get('/search', async (ctx) => {
  const { query } = ctx.query;

  const sanitizedQuery = validateAndSanitizeInput(query);
  if (!sanitizedQuery) {
    ctx.status = 400;
    ctx.body = { error: 'Search query is required and must be a non-empty string' };
    return;
  }

  const products = await db.all('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', [`%${sanitizedQuery}%`, `%${sanitizedQuery}%`]);

  ctx.status = 200;
  ctx.body = {
    results: products.map(product => {
      try {
        return {
          name: product.name,
          ...JSON.parse(product.data)
        };
      } catch (err) {
        return { name: product.name, data: 'Invalid JSON data' };
      }
    })
  };
});

app.use(router.routes()).use(router.allowedMethods());

initDb().then(() => {
  app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
  });
});