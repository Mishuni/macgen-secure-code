const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const csvParser = require('csv-parser');

dotenv.config();

const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

fastify.register(require('@fastify/cookie'));

fastify.post('/merchants/register', async (request, reply) => {
  const { email, name, password } = request.body;
  if (!email || !name || !password) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  const db = await dbPromise;
  await db.run('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', [email, name, password]);
  reply.status(201).send();
});

fastify.post('/merchants/login', async (request, reply) => {
  const { email, password } = request.body;
  const db = await dbPromise;
  const merchant = await db.get('SELECT * FROM merchants WHERE email = ? AND password = ?', [email, password]);

  if (!merchant) {
    return reply.status(401).send({ error: 'Invalid email or password' });
  }

  reply.setCookie('AUTH_COOKIE', 'some_auth_value', { path: '/' });
  reply.send('Login successful');
});

fastify.post('/merchants/upload-wares', async (request, reply) => {
  const { csv } = request.body;
  if (!csv) {
    return reply.status(400).send({ error: 'Invalid CSV format' });
  }

  const db = await dbPromise;
  const wares = [];

  csv.split('\n').forEach(line => {
    const [name, description, price] = line.split(',');
    if (name && description && price) {
      wares.push({ name, description, price });
    }
  });

  for (const ware of wares) {
    await db.run('INSERT INTO wares (name, description, price) VALUES (?, ?, ?)', [ware.name, ware.description, ware.price]);
  }

  reply.send('Wares uploaded successfully');
});

fastify.get('/wares', async (request, reply) => {
  const { minPrice, maxPrice } = request.query;
  const db = await dbPromise;

  const wares = await db.all('SELECT * FROM wares WHERE (price >= ? OR ? IS NULL) AND (price <= ? OR ? IS NULL)', [minPrice, minPrice, maxPrice, maxPrice]);

  let html = '<table><tr><th>Name</th><th>Description</th><th>Price</th></tr>';
  wares.forEach(ware => {
    html += `<tr><td>${ware.name}</td><td>${ware.description}</td><td>${ware.price}</td></tr>`;
  });
  html += '</table>';

  reply.type('text/html').send(html);
});

const start = async () => {
  const db = await dbPromise;
  await db.exec('CREATE TABLE IF NOT EXISTS merchants (id INTEGER PRIMARY KEY, email TEXT, name TEXT, password TEXT)');
  await db.exec('CREATE TABLE IF NOT EXISTS wares (id INTEGER PRIMARY KEY, name TEXT, description TEXT, price REAL)');

  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();