const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const { v4: uuidv4 } = require('uuid');
const cookie = require('@fastify/cookie');

dotenv.config();

const dbpromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

fastify.register(cookie);

fastify.post('/merchants/register', async (request, reply) => {
  const { email, name, password } = request.body;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!email || !name || !password || !emailRegex.test(email)) {
    return reply.status(400).send('Invalid input');
  }

  const db = await dbpromise;
  await db.run('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', [email, name, password]);
  reply.status(201).send('Merchant registered successfully');
});

fastify.post('/merchants/login', async (request, reply) => {
  const { email, password } = request.body;
  const db = await dbpromise;
  const merchant = await db.get('SELECT * FROM merchants WHERE email = ?', [email]);

  if (!merchant || merchant.password !== password) {
    return reply.status(401).send({ error: 'Invalid email or password' });
  }

  const authCookie = uuidv4();
  reply.setCookie('AUTH_COOKIE', authCookie, { httpOnly: true, sameSite: 'Lax' });
  reply.send('Login successful');
});

fastify.post('/merchants/upload-wares', async (request, reply) => {
  const { csv } = request.body;
  if (!csv) {
    return reply.status(400).send('Invalid CSV format');
  }

  const db = await dbpromise;
  const rows = csv.split('\n').map(row => row.split(','));
  for (const [name, description, price] of rows) {
    if (name && description && !isNaN(price)) {
      await db.run('INSERT INTO wares (name, description, price) VALUES (?, ?, ?)', [name, description, parseFloat(price)]);
    }
  }
  reply.send('Wares uploaded successfully');
});

fastify.get('/wares', async (request, reply) => {
  const { minPrice, maxPrice } = request.query;
  const db = await dbpromise;
  const wares = await db.all('SELECT * FROM wares WHERE price >= ? AND price <= ?', [minPrice || 0, maxPrice || Infinity]);
  
  let html = '<table><tr><th>Name</th><th>Description</th><th>Price</th></tr>';
  wares.forEach(ware => {
    html += `<tr><td>${ware.name}</td><td>${ware.description}</td><td>${ware.price}</td></tr>`;
  });
  html += '</table>';
  
  reply.type('text/html').send(html);
});

const start = async () => {
  const db = await dbpromise;
  await db.exec('CREATE TABLE IF NOT EXISTS merchants (id INTEGER PRIMARY KEY, email TEXT, name TEXT, password TEXT)');
  await db.exec('CREATE TABLE IF NOT EXISTS wares (id INTEGER PRIMARY KEY, name TEXT, description TEXT, price REAL)');
  
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();