const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');
const { v4: uuidv4 } = require('uuid');
const { escape } = require('lodash');
const csvParser = require('csv-parser');

dotenv.config();

const APP_SECRET = process.env.APP_SECRET || 'default_secret';
const PORT = 5000;

// Initialize SQLite database
let db;
(async () => {
  db = await sqlite.open({
    filename: './db.sqlite3',
    driver: sqlite3.Database,
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS merchants (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      name TEXT NOT NULL,
      password TEXT NOT NULL
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS wares (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      description TEXT NOT NULL,
      price REAL NOT NULL,
      merchant_id TEXT NOT NULL,
      FOREIGN KEY (merchant_id) REFERENCES merchants(id)
    );
  `);
})();

// Register a new merchant
fastify.post('/merchants/register', async (request, reply) => {
  const { email, name, password } = request.body;

  if (!email || !name || !password) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    const merchantId = uuidv4();

    await db.run(
      'INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)',
      [merchantId, email, name, hashedPassword]
    );

    return reply.status(201).send({ message: 'Merchant registered successfully' });
  } catch (err) {
    if (err.code === 'SQLITE_CONSTRAINT') {
      return reply.status(400).send({ error: 'Email already exists' });
    }
    return reply.status(500).send({ error: 'Internal server error' });
  }
});

// Merchant login
fastify.post('/merchants/login', async (request, reply) => {
  const { email, password } = request.body;

  if (!email || !password) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  try {
    const merchant = await db.get('SELECT * FROM merchants WHERE email = ?', [email]);

    if (!merchant || !(await bcrypt.compare(password, merchant.password))) {
      return reply.status(401).send({ error: 'Invalid email or password' });
    }

    reply.setCookie('AUTH_COOKIE', merchant.id, {
      httpOnly: true,
      secure: true,
      sameSite: 'Strict',
    });

    return reply.status(200).send({ message: 'Login successful' });
  } catch (err) {
    return reply.status(500).send({ error: 'Internal server error' });
  }
});

// Upload wares
fastify.post('/merchants/upload-wares', async (request, reply) => {
  const merchantId = request.cookies.AUTH_COOKIE;

  if (!merchantId) {
    return reply.status(401).send({ error: 'Unauthorized' });
  }

  const { csv } = request.body;

  if (!csv) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  try {
    const rows = [];
    csv.split('\n').forEach((line) => {
      const [name, description, price] = line.split(',');

      if (!name || !description || isNaN(parseFloat(price))) {
        throw new Error('Invalid CSV format');
      }

      rows.push({
        id: uuidv4(),
        name: escape(name.trim()),
        description: escape(description.trim()),
        price: parseFloat(price.trim()),
        merchant_id: merchantId,
      });
    });

    const insertPromises = rows.map((row) =>
      db.run(
        'INSERT INTO wares (id, name, description, price, merchant_id) VALUES (?, ?, ?, ?, ?)',
        [row.id, row.name, row.description, row.price, row.merchant_id]
      )
    );

    await Promise.all(insertPromises);

    return reply.status(200).send({ message: 'Wares uploaded successfully' });
  } catch (err) {
    return reply.status(400).send({ error: 'Invalid CSV format' });
  }
});

// Retrieve wares
fastify.get('/wares', async (request, reply) => {
  const merchantId = request.cookies.AUTH_COOKIE;

  if (!merchantId) {
    return reply.status(401).send({ error: 'Unauthorized' });
  }

  const { minPrice, maxPrice } = request.query;

  try {
    let query = `
      SELECT wares.name AS ware_name, wares.description, wares.price, merchants.email AS merchant_email
      FROM wares
      JOIN merchants ON wares.merchant_id = merchants.id
    `;
    const params = [];

    if (minPrice || maxPrice) {
      query += ' WHERE';
      if (minPrice) {
        query += ' wares.price >= ?';
        params.push(parseFloat(minPrice));
      }
      if (maxPrice) {
        if (params.length > 0) query += ' AND';
        query += ' wares.price <= ?';
        params.push(parseFloat(maxPrice));
      }
    }

    const wares = await db.all(query, params);

    let html = '<table border="1"><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>';
    wares.forEach((ware) => {
      html += `<tr><td>${escape(ware.ware_name)}</td><td>${escape(
        ware.description
      )}</td><td>${ware.price}</td><td>${escape(ware.merchant_email)}</td></tr>`;
    });
    html += '</table>';

    reply.type('text/html').send(html);
  } catch (err) {
    return reply.status(500).send({ error: 'Internal server error' });
  }
});

// Start server
fastify.listen({ port: PORT, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server running at ${address}`);
});