import fastify from 'fastify';
import { v4 as uuidv4 } from 'uuid';
import bcrypt from 'bcrypt';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';

dotenv.config();

const app = fastify();
const dbPromise = open({
  filename: process.env.DB_FILENAME || 'db.sqlite3',
  driver: sqlite3.Database
});

const SALT_ROUNDS = 10;
const INVITE_EXPIRATION_DAYS = 7;

async function setupDatabase() {
  const db = await dbPromise;
  await db.exec(`
    CREATE TABLE IF NOT EXISTS invitations (
      email TEXT PRIMARY KEY,
      invite_id TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS users (
      user_name TEXT PRIMARY KEY,
      password TEXT NOT NULL
    );
  `);
}

app.post('/invite_user', async (request, reply) => {
  const { email } = request.body;
  const db = await dbPromise;

  let invite = await db.get('SELECT invite_id FROM invitations WHERE email = ?', email);
  if (!invite) {
    const invite_id = uuidv4();
    await db.run('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', email, invite_id);
    invite = { invite_id };
  }

  // Send invite_id via a secure channel (e.g., email) instead of including it in the response
  reply.send({ message: 'Invitation created or retrieved successfully. Check your email for the invite ID.' });
});

app.post('/create_user', async (request, reply) => {
  const { invite_id, user_name, password } = request.body;
  const db = await dbPromise;

  const invite = await db.get('SELECT * FROM invitations WHERE invite_id = ? AND created_at > datetime("now", ?)', invite_id, `-${INVITE_EXPIRATION_DAYS} days`);
  if (!invite) {
    reply.status(401).send({ message: 'Invalid or expired invite_id' });
    return;
  }

  const existingUser = await db.get('SELECT * FROM users WHERE user_name = ?', user_name);
  if (existingUser) {
    reply.status(400).send({ message: 'User creation failed.' });
    return;
  }

  // Implement a stronger password policy
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
  if (!passwordRegex.test(password)) {
    reply.status(400).send({ message: 'Password must be at least 8 characters long and include uppercase, lowercase, number, and special character.' });
    return;
  }

  const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);
  await db.run('INSERT INTO users (user_name, password) VALUES (?, ?)', user_name, hashedPassword);
  reply.send({ message: 'User created successfully.' });
});

const start = async () => {
  try {
    await setupDatabase();
    await app.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server listening on http://0.0.0.0:5000');
  } catch (err) {
    console.error(err);
    process.exit(1);
  }
};

start();