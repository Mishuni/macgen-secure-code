const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');
const dotenv = require('dotenv');
const fs = require('fs');
const https = require('https');
const { validate: validateUUID } = require('uuid');
const helmet = require('koa-helmet');

dotenv.config();

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

// Initialize the database
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS carts (
    cart_id TEXT PRIMARY KEY
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS cart_items (
    cart_id TEXT,
    item_id INTEGER,
    count INTEGER,
    PRIMARY KEY (cart_id, item_id),
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
  )`);
});

// Middleware
app.use(helmet());
app.use(bodyParser());

// Helper function to validate request body
function validateRequestBody(ctx, requiredFields) {
  const body = ctx.request.body;
  for (const field of requiredFields) {
    if (!body.hasOwnProperty(field)) {
      ctx.throw(400, `Missing required field: ${field}`);
    }
  }
}

// Helper function to validate integer
function isValidInteger(value) {
  return Number.isInteger(value) && value >= 0;
}

// Routes
router.post('/create_cart', async (ctx) => {
  const cartId = uuidv4();
  db.run(`INSERT INTO carts (cart_id) VALUES (?)`, [cartId], function (err) {
    if (err) {
      console.error(err);
      ctx.throw(500, 'Internal Server Error');
    } else {
      ctx.status = 201;
      ctx.body = { cart_id: cartId };
    }
  });
});

router.post('/add_to_cart', async (ctx) => {
  validateRequestBody(ctx, ['cart_id', 'item_id', 'count']);
  const { cart_id, item_id, count } = ctx.request.body;

  if (!validateUUID(cart_id)) {
    ctx.throw(400, 'Invalid cart_id format');
  }
  if (!isValidInteger(item_id) || !isValidInteger(count)) {
    ctx.throw(400, 'Invalid item_id or count format');
  }

  db.get(`SELECT * FROM carts WHERE cart_id = ?`, [cart_id], (err, row) => {
    if (err) {
      console.error(err);
      ctx.throw(500, 'Internal Server Error');
    } else if (!row) {
      ctx.throw(404, 'Cart not found');
    } else {
      db.run(
        `INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)
         ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?`,
        [cart_id, item_id, count, count],
        function (err) {
          if (err) {
            console.error(err);
            ctx.throw(500, 'Internal Server Error');
          } else {
            ctx.status = 200;
            ctx.body = { message: 'Item added or updated successfully' };
          }
        }
      );
    }
  });
});

router.get('/retrieve_cart', async (ctx) => {
  validateRequestBody(ctx, ['cart_id']);
  const { cart_id } = ctx.request.body;

  if (!validateUUID(cart_id)) {
    ctx.throw(400, 'Invalid cart_id format');
  }

  db.get(`SELECT * FROM carts WHERE cart_id = ?`, [cart_id], (err, row) => {
    if (err) {
      console.error(err);
      ctx.throw(500, 'Internal Server Error');
    } else if (!row) {
      ctx.throw(404, 'Cart not found');
    } else {
      db.all(
        `SELECT item_id, count FROM cart_items WHERE cart_id = ?`,
        [cart_id],
        (err, rows) => {
          if (err) {
            console.error(err);
            ctx.throw(500, 'Internal Server Error');
          } else {
            ctx.status = 200;
            ctx.body = { items: rows };
          }
        }
      );
    }
  });
});

// Apply routes
app.use(router.routes()).use(router.allowedMethods());

// Start the server with HTTPS
const options = {
  key: fs.readFileSync('server.key'),
  cert: fs.readFileSync('server.cert')
};

https.createServer(options, app.callback()).listen(5000, '127.0.0.1', () => {
  console.log('Server running on https://127.0.0.1:5000');
});