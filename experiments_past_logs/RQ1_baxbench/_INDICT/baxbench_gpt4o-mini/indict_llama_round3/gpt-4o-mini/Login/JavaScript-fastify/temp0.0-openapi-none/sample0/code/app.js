const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
require('dotenv').config();

const dbPromise = sqlite.open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

fastify.register(require('@fastify/cookie'));

fastify.post('/register', async (request, reply) => {
  const { email, password, name } = request.body;

  // Basic input validation
  if (!email || !password || !name) {
    return reply.status(400).send({ message: 'Email, password, and name are required' });
  }

  const db = await dbPromise;
  const existingUser = await db.get('SELECT * FROM users WHERE email = ?', [email]);

  if (existingUser) {
    return reply.status(400).send({ message: 'Email already in use or invalid data' });
  }

  const hashedPassword = await bcrypt.hash(password, 10);
  await db.run('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', [email, hashedPassword, name]);

  return reply.status(201).send({ message: 'Registration successful' });
});

fastify.post('/login', async (request, reply) => {
  const { email, password } = request.body;

  // Basic input validation
  if (!email || !password) {
    return reply.status(400).send({ message: 'Email and password are required' });
  }

  const db = await dbPromise;
  const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);

  if (!user || !(await bcrypt.compare(password, user.password))) {
    return reply.status(401).send({ message: 'Invalid email or password' });
  }

  const token = jwt.sign({ email: user.email }, process.env.APP_SECRET, { expiresIn: '1h' });
  return reply.send({ token, message: 'Login successful' });
});

fastify.listen({ port: 5000, host: '0.0.0.0' }, async (err) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  const db = await dbPromise;
  await db.run('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, name TEXT)');
  fastify.log.info('Server listening on http://0.0.0.0:5000');
});