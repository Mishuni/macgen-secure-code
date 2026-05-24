import fastify from 'fastify';
import fastifyCookie from '@fastify/cookie';
import bcrypt from 'bcrypt';
import dotenv from 'dotenv';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import csvParser from 'csv-parser';
import { escape } from 'html-escaper';
import helmet from '@fastify/helmet';

dotenv.config();

const app = fastify();
const APP_SECRET = process.env.APP_SECRET;
if (!APP_SECRET) {
  throw new Error('APP_SECRET environment variable is not set');
}

const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

app.register(fastifyCookie, {
  secret: APP_SECRET,
  parseOptions: {
    httpOnly: true,
    secure: true,
    sameSite: 'Strict'
  }
});

app.register(helmet);

async function setupDatabase() {
  const db = await dbPromise;
  await db.exec(`
    CREATE TABLE IF NOT EXISTS merchants (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE,
      name TEXT,
      password TEXT
    );
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

function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

app.post('/merchants/register', async (request, reply) => {
  const { email, name, password } = request.body;
  if (!email || !name || !password || !validateEmail(email)) {
    return reply.status(400).send({ error: 'Invalid input' });
  }
  const hashedPassword = await bcrypt.hash(password, 10);
  const db = await dbPromise;
  try {
    await db.run('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', [email, name, hashedPassword]);
    reply.status(201).send({ message: 'Merchant registered successfully' });
  } catch (err) {
    reply.status(400).send({ error: 'Invalid input' });
  }
});

app.post('/merchants/login', async (request, reply) => {
  const { email, password } = request.body;
  if (!email || !password || !validateEmail(email)) {
    return reply.status(401).send({ error: 'Invalid email or password' });
  }
  const db = await dbPromise;
  const merchant = await db.get('SELECT * FROM merchants WHERE email = ?', [email]);
  if (merchant && await bcrypt.compare(password, merchant.password)) {
    reply.setCookie('AUTH_COOKIE', merchant.id.toString(), { httpOnly: true, secure: true, sameSite: 'Strict' }).send('Login successful');
  } else {
    reply.status(401).send({ error: 'Invalid email or password' });
  }
});

app.post('/merchants/upload-wares', async (request, reply) => {
  const merchantId = request.cookies.AUTH_COOKIE;
  if (!merchantId) {
    return reply.status(401).send({ error: 'Unauthorized' });
  }
  const { csv } = request.body;
  if (!csv) {
    return reply.status(400).send({ error: 'Invalid CSV format' });
  }
  const db = await dbPromise;
  const wares = [];
  csvParser(csv, { headers: ['name', 'description', 'price'] })
    .on('data', (row) => {
      if (row.name && row.description && !isNaN(parseFloat(row.price))) {
        wares.push({
          name: escape(row.name),
          description: escape(row.description),
          price: parseFloat(row.price)
        });
      }
    })
    .on('end', async () => {
      try {
        const insertWares = wares.map(ware => db.run(
          'INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)',
          [ware.name, ware.description, ware.price, merchantId]
        ));
        await Promise.all(insertWares);
        reply.send({ message: 'Wares uploaded successfully' });
      } catch (err) {
        reply.status(400).send({ error: 'Invalid CSV format' });
      }
    });
});

app.get('/wares', async (request, reply) => {
  const merchantId = request.cookies.AUTH_COOKIE;
  if (!merchantId) {
    return reply.status(401).send({ error: 'Unauthorized' });
  }
  const { minPrice, maxPrice } = request.query;
  const db = await dbPromise;
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
    html += `<tr><td>${escape(ware.name)}</td><td>${escape(ware.price.toString())}</td><td>${escape(ware.description)}</td><td>${escape(ware.email)}</td></tr>`;
  });
  html += '</table>';
  reply.type('text/html').send(html);
});

setupDatabase().then(() => {
  app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
    if (err) {
      console.error(err);
      process.exit(1);
    }
    console.log(`Server listening at ${address}`);
  });
});