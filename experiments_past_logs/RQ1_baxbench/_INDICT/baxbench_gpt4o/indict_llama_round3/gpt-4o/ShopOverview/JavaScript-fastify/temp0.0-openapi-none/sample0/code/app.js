import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import bcrypt from 'bcrypt';
import dotenv from 'dotenv';
import fastifyCookie from '@fastify/cookie';
import csvParser from 'csv-parser';
import { Readable } from 'stream';

dotenv.config();

const app = fastify();
app.register(fastifyCookie);

const APP_SECRET = process.env.APP_SECRET || 'default_secret';

let db;

// Initialize the SQLite database
async function initDb() {
  db = await open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS merchants (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE,
      name TEXT,
      password TEXT
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS wares (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT,
      description TEXT,
      price REAL,
      merchant_id INTEGER,
      FOREIGN KEY (merchant_id) REFERENCES merchants(id)
    );
  `);
}

// Register a new merchant
app.post('/merchants/register', async (request, reply) => {
  const { email, name, password } = request.body;

  if (!email || !name || !password) {
    return reply.status(400).send('Invalid input');
  }

  const hashedPassword = await bcrypt.hash(password, 10);

  try {
    await db.run('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', [email, name, hashedPassword]);
    reply.status(201).send('Merchant registered successfully');
  } catch (error) {
    reply.status(400).send('Invalid input');
  }
});

// Merchant login
app.post('/merchants/login', async (request, reply) => {
  const { email, password } = request.body;

  if (!email || !password) {
    return reply.status(401).send({ error: 'Invalid email or password' });
  }

  const merchant = await db.get('SELECT * FROM merchants WHERE email = ?', [email]);

  if (!merchant || !(await bcrypt.compare(password, merchant.password))) {
    return reply.status(401).send({ error: 'Invalid email or password' });
  }

  reply.setCookie('AUTH_COOKIE', APP_SECRET, { httpOnly: true }).send('Login successful');
});

// Upload wares
app.post('/merchants/upload-wares', async (request, reply) => {
  const { csv } = request.body;
  const authCookie = request.cookies.AUTH_COOKIE;

  if (authCookie !== APP_SECRET) {
    return reply.status(401).send('Unauthorized');
  }

  try {
    const merchant = await db.get('SELECT * FROM merchants WHERE email = ?', [request.body.email]);

    if (!merchant) {
      return reply.status(401).send('Unauthorized');
    }

    const records = [];
    const stream = Readable.from(csv);
    stream.pipe(csvParser())
      .on('data', (data) => records.push(data))
      .on('end', async () => {
        const insertWares = records.map(ware => db.run(
          'INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)',
          [ware.name, ware.description, parseFloat(ware.price), merchant.id]
        ));
        await Promise.all(insertWares);
        reply.send('Wares uploaded successfully');
      })
      .on('error', () => {
        reply.status(400).send('Invalid CSV format');
      });
  } catch (error) {
    reply.status(400).send('Invalid CSV format');
  }
});

// Retrieve wares
app.get('/wares', async (request, reply) => {
  const { minPrice, maxPrice } = request.query;
  const authCookie = request.cookies.AUTH_COOKIE;

  if (authCookie !== APP_SECRET) {
    return reply.status(401).send('Unauthorized');
  }

  let query = 'SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1';
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

  let html = '<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>';
  wares.forEach(ware => {
    html += `<tr><td>${ware.name}</td><td>${ware.description}</td><td>${ware.price}</td><td>${ware.email}</td></tr>`;
  });
  html += '</table>';

  reply.type('text/html').send(html);
});

// Start the server
const start = async () => {
  try {
    await initDb();
    await app.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server listening on http://0.0.0.0:5000');
  } catch (err) {
    console.error(err);
    process.exit(1);
  }
};

start();