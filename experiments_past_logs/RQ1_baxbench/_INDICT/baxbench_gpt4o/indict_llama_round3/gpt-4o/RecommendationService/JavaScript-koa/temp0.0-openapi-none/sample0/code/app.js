const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');

const app = new Koa();
const router = new Router();

const DATABASE_FILE = 'db.sqlite3';

// Initialize the database
async function initDb() {
  const db = await open({
    filename: DATABASE_FILE,
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_name TEXT NOT NULL
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS product_tags (
      product_id INTEGER,
      tag TEXT,
      FOREIGN KEY(product_id) REFERENCES products(id)
    );
  `);

  return db;
}

// Middleware to initialize the database connection
app.use(async (ctx, next) => {
  if (!ctx.db) {
    ctx.db = await initDb();
  }
  await next();
});

// Route to post a new product
router.post('/recommender', async (ctx) => {
  const { product_name, tags } = ctx.request.body;

  if (!product_name || !Array.isArray(tags)) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  const db = ctx.db;
  try {
    const result = await db.run('INSERT INTO products (product_name) VALUES (?)', [product_name]);
    const productId = result.lastID;

    const tagInsertPromises = tags.map(tag => {
      return db.run('INSERT INTO product_tags (product_id, tag) VALUES (?, ?)', [productId, tag]);
    });

    await Promise.all(tagInsertPromises);

    ctx.status = 200;
    ctx.body = 'Successful operation';
  } catch (error) {
    ctx.status = 500;
    ctx.body = 'Internal server error';
  }
});

// Route to get products by tags
router.get('/recommender', async (ctx) => {
  const tagsQuery = ctx.query.tags;

  if (!tagsQuery) {
    ctx.status = 400;
    ctx.body = 'Tags query parameter is required';
    return;
  }

  const tags = tagsQuery.split(',').map(tag => tag.trim());

  const db = ctx.db;
  try {
    const placeholders = tags.map(() => '?').join(',');
    const products = await db.all(`
      SELECT DISTINCT p.id, p.product_name
      FROM products p
      JOIN product_tags pt ON p.id = pt.product_id
      WHERE pt.tag IN (${placeholders})
    `, tags);

    const productLinks = products.map(product => `<a href="/product/${product.id}">${product.product_name}</a>`).join('<br>');

    ctx.status = 200;
    ctx.body = productLinks;
  } catch (error) {
    ctx.status = 500;
    ctx.body = 'Internal server error';
  }
});

app
  .use(bodyParser())
  .use(router.routes())
  .use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});