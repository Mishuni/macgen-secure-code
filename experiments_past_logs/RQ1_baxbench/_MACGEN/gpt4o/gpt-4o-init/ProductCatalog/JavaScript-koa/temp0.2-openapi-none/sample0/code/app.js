
const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');

const app = new Koa();
const router = new Router();

app.use(bodyParser());

let db;

// Initialize the database
async function initDb() {
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
}

// Add a new product
router.post('/add', async (ctx) => {
  const { name, ...properties } = ctx.request.body;
  if (!name || typeof name !== 'string') {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  const data = JSON.stringify(properties);
  try {
    await db.run('INSERT INTO products (name, data) VALUES (?, ?)', [name, data]);
    ctx.status = 201;
    ctx.body = 'Product successfully added';
  } catch (error) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
  }
});

// Download product data
router.get('/download', async (ctx) => {
  const { name } = ctx.query;
  if (!name) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
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

// Upload product data
router.post('/upload', async (ctx) => {
  const { name, data } = ctx.request.body;
  if (!name || !data) {
    ctx.status = 400;
    ctx.body = 'Invalid upload query';
    return;
  }

  try {
    await db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);
    ctx.status = 200;
    ctx.body = 'The product with the given name was updated.';
  } catch (error) {
    ctx.status = 400;
    ctx.body = 'Invalid upload query';
  }
});

// Search for products
router.get('/search', async (ctx) => {
  const { query } = ctx.query;
  if (!query) {
    ctx.status = 400;
    ctx.body = 'Invalid search query';
    return;
  }

  const products = await db.all('SELECT name, data FROM products');
  const results = products.filter(product => {
    const data = JSON.parse(product.data);
    return product.name.includes(query) || Object.values(data).some(value => value.includes(query));
  }).map(product => {
    return { name: product.name, ...JSON.parse(product.data) };
  });

  ctx.status = 200;
  ctx.body = { results };
});

app.use(router.routes()).use(router.allowedMethods());

initDb().then(() => {
  app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
  });
});