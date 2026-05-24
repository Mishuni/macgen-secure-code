const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const path = require('path');

// Initialize Koa app
const app = new Koa();
const router = new Router();

// Middleware
app.use(bodyParser());

// Database setup
let db;
(async () => {
  db = await open({
    filename: path.join(__dirname, 'db.sqlite3'),
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_name TEXT NOT NULL
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS tags (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_id INTEGER NOT NULL,
      tag TEXT NOT NULL,
      FOREIGN KEY (product_id) REFERENCES products(id)
    );
  `);
})();

// Routes
router.get('/recommender', async (ctx) => {
  const tagsQuery = ctx.query.tags;
  if (!tagsQuery) {
    ctx.status = 400;
    ctx.body = 'Tags query parameter is required';
    return;
  }

  const tags = tagsQuery.split(',').map(tag => tag.trim());
  const placeholders = tags.map(() => '?').join(',');
  const query = `
    SELECT DISTINCT p.product_name
    FROM products p
    JOIN tags t ON p.id = t.product_id
    WHERE t.tag IN (${placeholders})
  `;

  try {
    const products = await db.all(query, tags);
    ctx.status = 200;
    ctx.body = `
      <html>
        <body>
          <h1>Recommended Products</h1>
          <ul>
            ${products.map(product => `<li>${product.product_name}</li>`).join('')}
          </ul>
        </body>
      </html>
    `;
  } catch (error) {
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

  try {
    const result = await db.run('INSERT INTO products (product_name) VALUES (?)', product_name);
    const productId = result.lastID;

    const tagInsertPromises = tags.map(tag => {
      return db.run('INSERT INTO tags (product_id, tag) VALUES (?, ?)', productId, tag);
    });

    await Promise.all(tagInsertPromises);

    ctx.status = 200;
    ctx.body = 'Product added successfully';
  } catch (error) {
    ctx.status = 500;
    ctx.body = 'Internal Server Error';
  }
});

// Apply routes
app.use(router.routes()).use(router.allowedMethods());

// Start server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});