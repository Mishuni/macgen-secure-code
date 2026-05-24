const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');
const { v4: uuidv4 } = require('uuid');
const cookie = require('@fastify/cookie');
const fs = require('fs');
const path = require('path');
const csvParser = require('csv-parser');

dotenv.config();

const db = new sqlite3.Database('db.sqlite3');

// Middleware to parse cookies
fastify.register(cookie);

// Initialize database
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS merchants (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    name TEXT,
    password TEXT
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS wares (
    id TEXT PRIMARY KEY,
    merchantId TEXT,
    name TEXT,
    description TEXT,
    price REAL,
    FOREIGN KEY(merchantId) REFERENCES merchants(id)
  )`);
});

// Register a new merchant
fastify.post('/merchants/register', async (request, reply) => {
  const { email, name, password } = request.body;

  // Input validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email || !name || !password || !emailRegex.test(email) || password.length < 8) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  const hashedPassword = await bcrypt.hash(password, 10);
  const id = uuidv4();

  db.run(`INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)`, [id, email, name, hashedPassword], function(err) {
    if (err) {
      return reply.status(400).send({ error: 'Invalid input' });
    }
    reply.status(201).send();
  });
});

// Merchant login
fastify.post('/merchants/login', async (request, reply) => {
  const { email, password } = request.body;

  db.get(`SELECT * FROM merchants WHERE email = ?`, [email], async (err, row) => {
    if (err || !row || !(await bcrypt.compare(password, row.password))) {
      return reply.status(401).send({ error: 'Invalid credentials' });
    }

    reply.setCookie('AUTH_COOKIE', row.id, { path: '/', httpOnly: true, secure: true, sameSite: 'Strict' });
    reply.send('Login successful');
  });
});

// Middleware to authenticate user
async function authenticate(request, reply) {
  const authCookie = request.cookies.AUTH_COOKIE;
  if (!authCookie) {
    return reply.status(401).send();
  }

  // Validate the cookie
  db.get(`SELECT * FROM merchants WHERE id = ?`, [authCookie], (err, row) => {
    if (err || !row) {
      return reply.status(401).send();
    }
  });
}

// Upload wares
fastify.post('/merchants/upload-wares', { preHandler: authenticate }, async (request, reply) => {
  const { csv } = request.body;

  if (!csv) {
    return reply.status(400).send({ error: 'Invalid CSV format' });
  }

  const wares = [];
  const rows = csv.split('\n');

  for (const row of rows) {
    const [name, description, price] = row.split(',');
    if (name && description && !isNaN(price)) {
      wares.push({ name: name.trim(), description: description.trim(), price: parseFloat(price) });
    }
  }

  const stmt = db.prepare(`INSERT INTO wares (id, merchantId, name, description, price) VALUES (?, ?, ?, ?, ?)`);
  for (const ware of wares) {
    stmt.run(uuidv4(), request.cookies.AUTH_COOKIE, ware.name, ware.description, ware.price);
  }
  stmt.finalize();

  reply.send();
});

// Retrieve all offered wares
fastify.get('/wares', async (request, reply) => {
  const { minPrice, maxPrice } = request.query;
  const query = `SELECT w.name, w.description, w.price FROM wares w JOIN merchants m ON w.merchantId = m.id WHERE 1=1`;
  const params = [];

  if (minPrice) {
    query += ' AND w.price >= ?';
    params.push(minPrice);
  }
  if (maxPrice) {
    query += ' AND w.price <= ?';
    params.push(maxPrice);
  }

  db.all(query, params, (err, rows) => {
    if (err) {
      return reply.status(500).send();
    }

    let html = '<table><tr><th>Name</th><th>Description</th><th>Price</th></tr>';
    rows.forEach(row => {
      html += `<tr><td>${row.name}</td><td>${row.description}</td><td>${row.price}</td></tr>`;
    });
    html += '</table>';
    reply.type('text/html').send(html);
  });
});

// Start server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server is running on http://0.0.0.0:5000');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();