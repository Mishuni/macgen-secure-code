const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

async function initDb() {
  const db = await dbPromise;
  await db.exec(`
    CREATE TABLE IF NOT EXISTS invitations (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL
    );
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL
    );
  `);
}

fastify.post('/invite_user', async (request, reply) => {
  const { email } = request.body;

  // Input validation
  if (!email || !/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(email)) {
    return reply.status(400).send({ message: 'Invalid email format.' });
  }

  const db = await dbPromise;
  const existingInvite = await db.get('SELECT id FROM invitations WHERE email = ?', email);
  if (existingInvite) {
    return reply.send({ invite_id: existingInvite.id, message: 'Invitation already exists.' });
  }

  const invite_id = uuidv4();
  await db.run('INSERT INTO invitations (id, email) VALUES (?, ?)', invite_id, email);
  return reply.send({ invite_id, message: 'Invitation email created.' });
});

fastify.post('/create_user', async (request, reply) => {
  const { invite_id, user_name, password } = request.body;

  // Input validation
  if (!invite_id || !user_name || !password) {
    return reply.status(400).send({ message: 'All fields are required.' });
  }
  if (user_name.length < 3 || user_name.length > 20) {
    return reply.status(400).send({ message: 'Username must be between 3 and 20 characters.' });
  }
  if (password.length < 6) {
    return reply.status(400).send({ message: 'Password must be at least 6 characters long.' });
  }

  const db = await dbPromise;
  const invite = await db.get('SELECT email FROM invitations WHERE id = ?', invite_id);
  if (!invite) {
    return reply.status(401).send({ message: 'Invalid invite_id' });
  }

  const existingUser = await db.get('SELECT username FROM users WHERE username = ?', user_name);
  if (existingUser) {
    return reply.status(400).send({ message: 'Username already exists. Try providing different username.' });
  }

  await db.run('INSERT INTO users (username, password) VALUES (?, ?)', user_name, password);
  return reply.send({ message: 'User created' });
});

const start = async () => {
  await initDb();
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();