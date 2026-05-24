const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const bcrypt = require('bcrypt');
require('dotenv').config();

const APP_SECRET = process.env.APP_SECRET || 'default_secret';

let db;

async function setupDatabase() {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS invitations (
      email TEXT PRIMARY KEY,
      invite_id TEXT NOT NULL
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      user_name TEXT PRIMARY KEY,
      password TEXT NOT NULL
    );
  `);
}

fastify.post('/invite_user', async (request, reply) => {
  const { email } = request.body;

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return reply.status(400).send({ message: 'Invalid email format' });
  }

  try {
    const existingInvite = await db.get('SELECT invite_id FROM invitations WHERE email = ?', [email]);

    if (existingInvite) {
      return reply.send({ invite_id: existingInvite.invite_id, message: 'Invitation already exists.' });
    }

    const invite_id = uuidv4();
    await db.run('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', [email, invite_id]);

    return reply.send({ invite_id, message: 'Invitation created successfully.' });
  } catch (error) {
    request.log.error(error);
    return reply.status(500).send({ message: 'Internal Server Error' });
  }
});

fastify.post('/create_user', async (request, reply) => {
  const { invite_id, user_name, password } = request.body;

  if (!invite_id || !user_name || !password) {
    return reply.status(400).send({ message: 'Missing required fields' });
  }

  try {
    const invite = await db.get('SELECT email FROM invitations WHERE invite_id = ?', [invite_id]);

    if (!invite) {
      return reply.status(401).send({ message: 'Invalid invite_id' });
    }

    const existingUser = await db.get('SELECT user_name FROM users WHERE user_name = ?', [user_name]);

    if (existingUser) {
      return reply.status(400).send({ message: 'Username already exists. Try providing different username.' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    await db.run('INSERT INTO users (user_name, password) VALUES (?, ?)', [user_name, hashedPassword]);

    return reply.send({ message: 'User created successfully.' });
  } catch (error) {
    request.log.error(error);
    return reply.status(500).send({ message: 'Internal Server Error' });
  }
});

const start = async () => {
  try {
    await setupDatabase();
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();