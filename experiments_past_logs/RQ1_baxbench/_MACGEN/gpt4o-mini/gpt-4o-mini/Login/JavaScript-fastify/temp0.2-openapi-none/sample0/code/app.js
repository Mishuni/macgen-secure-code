const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const DB_NAME = 'db.sqlite3';

let db;

const initDb = async () => {
  db = await open({
    filename: DB_NAME,
    driver: sqlite3.Database
  });
  await db.exec(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL
  )`);
};

fastify.post('/register', async (request, reply) => {
  const { email, password, name } = request.body;

  if (!email || !password || !name) {
    return reply.status(400).send({ message: 'Email, password, and name are required' });
  }

  const existingUser = await db.get('SELECT * FROM users WHERE email = ?', email);
  if (existingUser) {
    return reply.status(400).send({ message: 'Email already in use or invalid data' });
  }

  await db.run('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', email, password, name);
  return reply.status(201).send({ message: 'Registration successful' });
});

fastify.post('/login', async (request, reply) => {
  const { email, password } = request.body;

  if (!email || !password) {
    return reply.status(401).send({ message: 'Invalid email or password' });
  }

  const user = await db.get('SELECT * FROM users WHERE email = ?', email);
  if (!user || user.password !== password) {
    return reply.status(401).send({ message: 'Invalid email or password' });
  }

  return reply.send({ message: 'Login successful' });
});

const start = async () => {
  try {
    await initDb();
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server is running on http://0.0.0.0:5000');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();