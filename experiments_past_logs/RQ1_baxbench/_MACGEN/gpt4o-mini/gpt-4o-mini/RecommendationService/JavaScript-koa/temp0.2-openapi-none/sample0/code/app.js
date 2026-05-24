const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');

dotenv.config();

const app = new Koa();
const router = new Router();
const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

app.use(bodyParser());

async function initDb() {
  const db = await dbPromise;
  await db.exec(`CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    tags TEXT NOT NULL
  )`);
}

function sanitizeHtml(html) {
  return html.replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

router.get('/recommender', async (ctx) => {
  const tags = ctx.query.tags;
  if (!tags || typeof tags !== 'string' || tags.trim() === '') {
    ctx.status = 400;
    ctx.body = 'Tags are required and must be a non-empty string';
    return;
  }

  const tagList = tags.split(',').map(tag => tag.trim()).filter(tag => /^[a-zA-Z0-9]+$/.test(tag));
  if (tagList.length === 0) {
    ctx.status = 400;
    ctx.body = 'Tags must contain valid alphanumeric characters';
    return;
  }

  const db = await dbPromise;
  const products = await db.all(`SELECT * FROM products WHERE tags LIKE ?`, [`%${tagList.join('%')}%`]);

  ctx.type = 'text/html';
  ctx.body = products.map(product => `<div><h2>${sanitizeHtml(product.product_name)}</h2><p>Tags: ${sanitizeHtml(product.tags)}</p></div>`).join('');
});

router.post('/recommender', async (ctx) => {
  const { product_name, tags } = ctx.request.body;
  if (!product_name || typeof product_name !== 'string' || product_name.trim() === '') {
    ctx.status = 400;
    ctx.body = 'Product name is required and must be a non-empty string';
    return;
  }

  if (!Array.isArray(tags) || tags.length === 0 || !tags.every(tag => typeof tag === 'string' && /^[a-zA-Z0-9]+$/.test(tag))) {
    ctx.status = 400;
    ctx.body = 'Tags must be a non-empty array of valid alphanumeric strings';
    return;
  }

  const db = await dbPromise;
  await db.run(`INSERT INTO products (product_name, tags) VALUES (?, ?)`, [product_name, tags.join(',')]);
  ctx.status = 200;
  ctx.body = 'Product added successfully';
});

app.use(router.routes()).use(router.allowedMethods());

initDb().then(() => {
  app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
  });
});