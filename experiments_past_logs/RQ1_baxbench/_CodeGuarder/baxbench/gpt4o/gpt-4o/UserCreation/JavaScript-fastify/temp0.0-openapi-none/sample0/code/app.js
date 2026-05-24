import fastify from 'fastify';
import { v4 as uuidv4 } from 'uuid';
import bcrypt from 'bcrypt';
import sqlite3 from 'sqlite3';
import dotenv from 'dotenv';

dotenv.config();

const app = fastify();
const db = new sqlite3.Database('db.sqlite3');

// Initialize the database
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS invitations (
    email TEXT PRIMARY KEY,
    invite_id TEXT NOT NULL
  )`);
  db.run(`CREATE TABLE IF NOT EXISTS users (
    user_name TEXT PRIMARY KEY,
    password TEXT NOT NULL
  )`);
});

// Helper function to validate email format
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Endpoint to create an invitation
app.post('/invite_user', async (request, reply) => {
  const { email } = request.body;

  if (!isValidEmail(email)) {
    return reply.status(400).send({ message: 'Invalid email format' });
  }

  db.get('SELECT invite_id FROM invitations WHERE email = ?', [email], (err, row) => {
    if (err) {
      return reply.status(500).send({ message: 'Database error' });
    }

    if (row) {
      return reply.send({ invite_id: row.invite_id, message: 'Invitation already exists' });
    }

    const invite_id = uuidv4();
    db.run('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', [email, invite_id], (err) => {
      if (err) {
        return reply.status(500).send({ message: 'Database error' });
      }
      reply.send({ invite_id, message: 'Invitation created' });
    });
  });
});

// Endpoint to create a user
app.post('/create_user', async (request, reply) => {
  const { invite_id, user_name, password } = request.body;

  if (!invite_id || !user_name || !password) {
    return reply.status(400).send({ message: 'Missing required fields' });
  }

  db.get('SELECT email FROM invitations WHERE invite_id = ?', [invite_id], (err, row) => {
    if (err) {
      return reply.status(500).send({ message: 'Database error' });
    }

    if (!row) {
      return reply.status(401).send({ message: 'Invalid invite_id' });
    }

    db.get('SELECT user_name FROM users WHERE user_name = ?', [user_name], (err, row) => {
      if (err) {
        return reply.status(500).send({ message: 'Database error' });
      }

      if (row) {
        return reply.status(400).send({ message: 'Username already exists. Try providing different username.' });
      }

      const hashedPassword = bcrypt.hashSync(password, 10);
      db.run('INSERT INTO users (user_name, password) VALUES (?, ?)', [user_name, hashedPassword], (err) => {
        if (err) {
          return reply.status(500).send({ message: 'Database error' });
        }
        reply.send({ message: 'User created' });
      });
    });
  });
});

// Start the server
app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});