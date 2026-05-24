const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');

const app = new Koa();
const router = new Router();

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      name TEXT PRIMARY KEY,
      data TEXT
    )
  `);
})();

// Middleware
app.use(bodyParser());

// Routes
router.post('/add', async (ctx) => {
  const { name, ...properties } = ctx.request.body;
  if (!name || typeof name !== 'string') {
    ctx.status = 400;
    ctx.body = 'Invalid input: name is required and must be a string';
    return;
  }

  const data = JSON.stringify(properties);
  try {
    await db.run('INSERT INTO products (name, data) VALUES (?, ?)', [name, data]);
    ctx.status = 201;
    ctx.body = 'Product successfully added';
  } catch (error) {
    ctx.status = 400;
    ctx.body = 'Invalid input: product with this name may already exist';
  }
});

router.get('/download', async (ctx) => {
  const { name } = ctx.query;
  if (!name || typeof name !== 'string') {
    ctx.status = 400;
    ctx.body = 'Invalid input: name is required and must be a string';
    return;
  }

  const product = await db.get('SELECT data FROM products WHERE name = ?', [name]);
  if (product) {
    ctx.status = 200;
    ctx.body = { data: product.data };
  } else {
    ctx.status = 400;
    ctx.body = 'Product not found';
  }
});

router.post('/upload', async (ctx) => {
  const { name, data } = ctx.request.body;
  if (!name || typeof name !== 'string' || !data || typeof data !== 'string') {
    ctx.status = 400;
    ctx.body = 'Invalid upload query: name and data are required and must be strings';
    return;
  }

  try {
    const result = await db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);
    if (result.changes === 0) {
      ctx.status = 400;
      ctx.body = 'Product not found';
    } else {
      ctx.status = 200;
      ctx.body = 'The product with the given name was updated.';
    }
  } catch (error) {
    ctx.status = 400;
    ctx.body = 'Invalid upload query';
  }
});

router.get('/search', async (ctx) => {
  const { query } = ctx.query;
  if (!query || typeof query !== 'string') {
    ctx.status = 400;
    ctx.body = 'Invalid search query: query is required and must be a string';
    return;
  }

  const products = await db.all('SELECT name, data FROM products');
  const results = products.filter(product => {
    try {
      const data = JSON.parse(product.data);
      return product.name.includes(query) || Object.values(data).some(value => value.includes(query));
    } catch (error) {
      return false;
    }
  }).map(product => {
    return { name: product.name, ...JSON.parse(product.data) };
  });

  ctx.status = 200;
  ctx.body = { results };
});

// Apply routes
app.use(router.routes()).use(router.allowedMethods());

// Start server
app.listen(5000, () => {
  console.log('Server running on http://0.0.0.0:5000');
});