const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
require('dotenv').config();

const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

fastify.register(require('@fastify/cookie'));

fastify.post('/register', async (request, reply) => {
  const { email, username, password } = request.body;

  if (!email || !username || !password) {
    return reply.status(400).send({ message: 'Email already in use or invalid data' });
  }

  const db = await dbPromise;
  const hashedPassword = await bcrypt.hash(password, 10);

  try {
    await db.run('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', [email, username, hashedPassword]);
    return reply.status(201).send({ message: 'Registration successful' });
  } catch (error) {
    return reply.status(400).send({ message: 'Email already in use or invalid data' });
  }
});

fastify.post('/login', async (request, reply) => {
  const { email, password } = request.body;

  const db = await dbPromise;
  const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);

  if (!user || !(await bcrypt.compare(password, user.password))) {
    return reply.status(401).send({ message: 'Invalid email or password' });
  }

  const token = jwt.sign({ username: user.username }, process.env.APP_SECRET);
  return reply.send({ token, message: 'Login successful' });
});

const authenticate = async (request, reply) => {
  const token = request.headers['authorization']?.split(' ')[1];
  if (!token) {
    return reply.status(401).send({ message: 'Invalid authentication token' });
  }

  try {
    const decoded = jwt.verify(token, process.env.APP_SECRET);
    request.user = decoded;
  } catch (err) {
    return reply.status(401).send({ message: 'Invalid authentication token' });
  }
};

fastify.post('/set_secret', { preHandler: authenticate }, async (request, reply) => {
  const { secret } = request.body;

  if (!secret) {
    return reply.status(400).send({ message: 'Secret is required' });
  }

  const db = await dbPromise;
  await db.run('INSERT INTO secrets (username, secret) VALUES (?, ?)', [request.user.username, secret]);
  return reply.send({ message: 'Secret has been set successfully' });
});

fastify.get('/get_secret', { preHandler: authenticate }, async (request, reply) => {
  const { username } = request.query;

  const db = await dbPromise;
  const secret = await db.get('SELECT secret FROM secrets WHERE username = ?', [username]);

  if (!secret) {
    return reply.status(404).send({ message: 'Secret not found' });
  }

  return reply.send({ secret: secret.secret });
});

const start = async () => {
  const db = await dbPromise;
  await db.exec('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT, username TEXT, password TEXT)');
  await db.exec('CREATE TABLE IF NOT EXISTS secrets (id INTEGER PRIMARY KEY, username TEXT, secret TEXT)');

  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();