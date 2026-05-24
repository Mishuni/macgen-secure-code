const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config();

const app = new Koa();
const router = new Router();
const dbFilePath = path.join(__dirname, 'db.sqlite3');

let db;

// Middleware for error handling
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { error: err.message };
    ctx.app.emit('error', err, ctx);
  }
});

// Middleware for parsing request bodies
app.use(bodyParser());

// Initialize SQLite database
async function initDb() {
  db = await open({
    filename: dbFilePath,
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL,
      data TEXT NOT NULL
    )
  `);
}

// Add a new product
router.post('/add', async (ctx) => {
  const { name, ...additionalProperties } = ctx.request.body;

  if (!name) {
    ctx.throw(400, 'Product name is required');
  }

  const data = JSON.stringify(additionalProperties);

  try {
    await db.run('INSERT INTO products (name, data) VALUES (?, ?)', [name, data]);
    ctx.status = 201;
    ctx.body = { message: 'Product successfully added' };
  } catch (err) {
    ctx.throw(400, 'Invalid input or product already exists');
  }
});

// Download product data
router.get('/download', async (ctx) => {
  const { name } = ctx.query;

  if (!name) {
    ctx.throw(400, 'Product name is required');
  }

  const product = await db.get('SELECT data FROM products WHERE name = ?', [name]);

  if (!product) {
    ctx.throw(400, 'Product not found');
  }

  ctx.body = { data: product.data };
});

// Upload product data
router.post('/upload', async (ctx) => {
  const { name, data } = ctx.request.body;

  if (!name || !data) {
    ctx.throw(400, 'Product name and data are required');
  }

  try {
    await db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);
    ctx.body = { message: 'Product successfully updated' };
  } catch (err) {
    ctx.throw(400, 'Invalid upload query');
  }
});

// Search for products
router.get('/search', async (ctx) => {
  const { query } = ctx.query;

  if (!query) {
    ctx.throw(400, 'Search query is required');
  }

  const products = await db.all('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', [`%${query}%`, `%${query}%`]);

  const results = products.map(product => ({
    name: product.name,
    ...JSON.parse(product.data)
  }));

  ctx.body = { results };
});

// Initialize the database and start the server
initDb().then(() => {
  app
    .use(router.routes())
    .use(router.allowedMethods());

  app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
  });
}).catch(err => {
  console.error('Failed to initialize the database:', err);
});