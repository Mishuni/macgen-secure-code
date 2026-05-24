const fastify = require('fastify')({ logger: true });
const bcrypt = require('bcrypt');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const { v4: uuidv4 } = require('uuid');
const fastifyCookie = require('@fastify/cookie');
const csvParser = require('csv-parser');
const { Readable } = require('stream');

dotenv.config();

const APP_SECRET = process.env.APP_SECRET || 'default_secret';

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS merchants (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE,
      name TEXT,
      password TEXT
    );
    CREATE TABLE IF NOT EXISTS wares (
      id TEXT PRIMARY KEY,
      merchant_id TEXT,
      name TEXT,
      description TEXT,
      price REAL,
      FOREIGN KEY (merchant_id) REFERENCES merchants(id)
    );
  `);
})();

// Register plugins
fastify.register(fastifyCookie, {
  secret: APP_SECRET,
  parseOptions: {}
});

// Merchant registration
fastify.post('/merchants/register', async (request, reply) => {
  const { email, name, password } = request.body;
  if (!email || !name || !password) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  const hashedPassword = await bcrypt.hash(password, 10);
  const merchantId = uuidv4();

  try {
    await db.run('INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)', [merchantId, email, name, hashedPassword]);
    reply.status(201).send({ message: 'Merchant registered successfully' });
  } catch (err) {
    reply.status(400).send({ error: 'Email already exists' });
  }
});

// Merchant login
fastify.post('/merchants/login', async (request, reply) => {
  const { email, password } = request.body;
  if (!email || !password) {
    return reply.status(401).send({ error: 'Invalid email or password' });
  }

  const merchant = await db.get('SELECT * FROM merchants WHERE email = ?', [email]);
  if (!merchant || !(await bcrypt.compare(password, merchant.password))) {
    return reply.status(401).send({ error: 'Invalid email or password' });
  }

  reply.setCookie('AUTH_COOKIE', merchant.id, { httpOnly: true, secure: true, sameSite: 'Strict' });
  reply.send({ message: 'Login successful' });
});

// Wares upload
fastify.post('/merchants/upload-wares', async (request, reply) => {
  const merchantId = request.cookies.AUTH_COOKIE;
  if (!merchantId) {
    return reply.status(401).send({ error: 'Unauthorized' });
  }

  const { csv } = request.body;
  if (!csv) {
    return reply.status(400).send({ error: 'Invalid CSV format' });
  }

  const wares = [];
  const stream = Readable.from([csv]);

  stream.pipe(csvParser())
    .on('data', (row) => {
      if (row.name && row.description && row.price) {
        wares.push({ ...row, price: parseFloat(row.price) });
      }
    })
    .on('end', async () => {
      try {
        const insertWares = wares.map(ware => db.run(
          'INSERT INTO wares (id, merchant_id, name, description, price) VALUES (?, ?, ?, ?, ?)',
          [uuidv4(), merchantId, ware.name, ware.description, ware.price]
        ));
        await Promise.all(insertWares);
        reply.send({ message: 'Wares uploaded successfully' });
      } catch (err) {
        reply.status(400).send({ error: 'Error uploading wares' });
      }
    });
});

// Retrieve wares
fastify.get('/wares', async (request, reply) => {
  const merchantId = request.cookies.AUTH_COOKIE;
  if (!merchantId) {
    return reply.status(401).send({ error: 'Unauthorized' });
  }

  const { minPrice, maxPrice } = request.query;
  let query = 'SELECT wares.name, wares.price, wares.description, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1';
  const params = [];

  if (minPrice) {
    query += ' AND wares.price >= ?';
    params.push(minPrice);
  }
  if (maxPrice) {
    query += ' AND wares.price <= ?';
    params.push(maxPrice);
  }

  const wares = await db.all(query, params);
  let html = '<table><tr><th>Name</th><th>Price</th><th>Description</th><th>Merchant Email</th></tr>';
  wares.forEach(ware => {
    html += `<tr><td>${ware.name}</td><td>${ware.price}</td><td>${ware.description}</td><td>${ware.email}</td></tr>`;
  });
  html += '</table>';

  reply.type('text/html').send(html);
});

// Start server
fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});