const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');
const csvParser = require('csv-parser');
const { Readable } = require('stream');
const { v4: uuidv4 } = require('uuid');
const fastifyCookie = require('@fastify/cookie');

dotenv.config();

const db = new sqlite3.Database('db.sqlite3', (err) => {
  if (err) {
    console.error('Could not connect to database', err);
  } else {
    console.log('Connected to database');
  }
});

db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS merchants (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    name TEXT,
    password TEXT
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS wares (
    id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    price REAL,
    merchant_id TEXT,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id)
  )`);
});

fastify.register(fastifyCookie, {
  secret: process.env.APP_SECRET,
  parseOptions: {}
});

fastify.post('/merchants/register', async (request, reply) => {
  const { email, name, password } = request.body;
  if (!email || !name || !password) {
    return reply.status(400).send('Invalid input');
  }

  const hashedPassword = await bcrypt.hash(password, 10);
  const merchantId = uuidv4();

  db.run(`INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)`, [merchantId, email, name, hashedPassword], function(err) {
    if (err) {
      return reply.status(400).send('Invalid input');
    }
    reply.status(201).send('Merchant registered successfully');
  });
});

fastify.post('/merchants/login', async (request, reply) => {
  const { email, password } = request.body;
  if (!email || !password) {
    return reply.status(401).send({ error: 'Invalid email or password' });
  }

  db.get(`SELECT * FROM merchants WHERE email = ?`, [email], async (err, merchant) => {
    if (err || !merchant) {
      return reply.status(401).send({ error: 'Invalid email or password' });
    }

    const match = await bcrypt.compare(password, merchant.password);
    if (!match) {
      return reply.status(401).send({ error: 'Invalid email or password' });
    }

    reply.setCookie('AUTH_COOKIE', merchant.id, { httpOnly: true, secure: false });
    reply.status(200).send('Login successful');
  });
});

fastify.post('/merchants/upload-wares', async (request, reply) => {
  const merchantId = request.cookies.AUTH_COOKIE;
  if (!merchantId) {
    return reply.status(401).send('Unauthorized');
  }

  const { csv } = request.body;
  if (!csv) {
    return reply.status(400).send('Invalid CSV format');
  }

  const wares = [];
  const stream = Readable.from(csv);

  stream.pipe(csvParser())
    .on('data', (row) => {
      if (row.name && row.description && row.price) {
        wares.push({ id: uuidv4(), ...row, merchant_id: merchantId });
      }
    })
    .on('end', () => {
      const stmt = db.prepare(`INSERT INTO wares (id, name, description, price, merchant_id) VALUES (?, ?, ?, ?, ?)`);
      wares.forEach(ware => {
        stmt.run(ware.id, ware.name, ware.description, parseFloat(ware.price), ware.merchant_id);
      });
      stmt.finalize();
      reply.status(200).send('Wares uploaded successfully');
    })
    .on('error', () => {
      reply.status(400).send('Invalid CSV format');
    });
});

fastify.get('/wares', async (request, reply) => {
  const merchantId = request.cookies.AUTH_COOKIE;
  if (!merchantId) {
    return reply.status(401).send('Unauthorized');
  }

  const { minPrice, maxPrice } = request.query;
  let query = `SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1`;
  const params = [];

  if (minPrice) {
    query += ` AND wares.price >= ?`;
    params.push(minPrice);
  }

  if (maxPrice) {
    query += ` AND wares.price <= ?`;
    params.push(maxPrice);
  }

  db.all(query, params, (err, rows) => {
    if (err) {
      return reply.status(500).send('Internal Server Error');
    }

    let html = '<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>';
    rows.forEach(row => {
      html += `<tr><td>${row.name}</td><td>${row.description}</td><td>${row.price}</td><td>${row.email}</td></tr>`;
    });
    html += '</table>';

    reply.type('text/html').send(html);
  });
});

fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});