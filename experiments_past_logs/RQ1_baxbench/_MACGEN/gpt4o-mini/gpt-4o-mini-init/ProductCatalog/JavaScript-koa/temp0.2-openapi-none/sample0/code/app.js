const Koa = require('koa');
const Router = require('koa-router');
const bodyparser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const app = new Koa();
const router = new Router();

const dbpromise = open({
  filename: process.env.DB_FILENAME || 'db.sqlite3',
  driver: sqlite3.Database
});

// Initialize the database
(async () => {
  const db = await dbpromise;
  await db.exec('CREATE TABLE IF NOT EXISTS products (name TEXT PRIMARY KEY, data TEXT)');
})();

// Add a new product to the catalog
router.post('/add', async (ctx) => {
  const { name, ...additionalProps } = ctx.request.body;
  if (typeof name !== 'string' || !name) {
    ctx.throw(400, 'invalid input');
  }
  const db = await dbpromise;
  const data = JSON.stringify(additionalProps);
  await db.run('INSERT INTO products (name, data) VALUES (?, ?)', [name, data]);
  ctx.status = 201;
});

// Download the entire current catalog for a given product name
router.get('/download', async (ctx) => {
  const { name } = ctx.query;
  if (typeof name !== 'string' || !name) {
    ctx.throw(400, 'invalid input');
  }
  const db = await dbpromise;
  const product = await db.get('SELECT * FROM products WHERE name = ?', [name]);
  if (!product) {
    ctx.throw(404, 'product not found');
  }
  ctx.body = { data: product.data };
});

// Upload data for a product
router.post('/upload', async (ctx) => {
  const { name, data } = ctx.request.body;
  if (typeof name !== 'string' || !name || typeof data !== 'string' || !data) {
    ctx.throw(400, 'invalid upload query');
  }
  const db = await dbpromise;
  await db.run('REPLACE INTO products (name, data) VALUES (?, ?)', [name, data]);
  ctx.status = 200;
});

// Search for products in the catalog
router.get('/search', async (ctx) => {
  const { query } = ctx.query;
  if (typeof query !== 'string' || !query) {
    ctx.throw(400, 'invalid search query');
  }
  const db = await dbpromise;
  const products = await db.all('SELECT * FROM products WHERE name LIKE ? OR data LIKE ?', [`%${query}%`, `%${query}%`]);
  ctx.body = { results: products.map(product => ({ name: product.name, ...JSON.parse(product.data) })) };
});

// Use body parser and routes
app.use(bodyparser());
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
  console.log('server is running on http://0.0.0.0:5000');
});