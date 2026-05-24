const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

// Initialize database
db.serialize(() => {
  db.run("CREATE TABLE IF NOT EXISTS carts (cart_id TEXT PRIMARY KEY)");
  db.run("CREATE TABLE IF NOT EXISTS cart_items (cart_id TEXT, item_id INTEGER, count INTEGER, PRIMARY KEY (cart_id, item_id))");
});

// Create a new shopping cart
router.post('/create_cart', async (ctx) => {
  const cart_id = uuidv4();
  db.run("INSERT INTO carts (cart_id) VALUES (?)", [cart_id]);
  ctx.status = 201;
  ctx.body = { cart_id };
});

// Add or remove items from the cart
router.post('/add_to_cart', async (ctx) => {
  const { cart_id, item_id, count } = ctx.request.body;
  if (!cart_id || !Number.isInteger(item_id) || !Number.isInteger(count)) {
    ctx.status = 400;
    ctx.body = { error: 'invalid request' };
    return;
  }
  db.get("SELECT * FROM carts WHERE cart_id = ?", [cart_id], (err, row) => {
    if (err || !row) {
      ctx.status = 404;
      ctx.body = { error: 'cart not found' };
      return;
    }
    db.run("INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?", [cart_id, item_id, count, count]);
    ctx.status = 200;
  });
});

// Retrieve all items in the cart
router.post('/retrieve_cart', async (ctx) => {
  const { cart_id } = ctx.request.body;
  if (!cart_id) {
    ctx.status = 400;
    ctx.body = { error: 'invalid request' };
    return;
  }
  db.get("SELECT * FROM carts WHERE cart_id = ?", [cart_id], (err, row) => {
    if (err || !row) {
      ctx.status = 404;
      ctx.body = { error: 'cart not found' };
      return;
    }
    db.all("SELECT item_id, count FROM cart_items WHERE cart_id = ?", [cart_id], (err, items) => {
      ctx.status = 200;
      ctx.body = { items: items || [] };
    });
  });
});

// Use the router
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
  console.log('server is running on http://0.0.0.0:5000');
});