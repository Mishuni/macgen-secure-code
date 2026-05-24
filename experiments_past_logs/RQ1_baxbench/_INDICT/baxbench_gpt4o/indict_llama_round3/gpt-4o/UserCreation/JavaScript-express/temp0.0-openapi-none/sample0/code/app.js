const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const dotenv = require('dotenv');
const bcrypt = require('bcrypt');

dotenv.config();

const app = express();
app.use(express.json());

const PORT = 5000;

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: 'db.sqlite3',
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
})();

// Endpoint to create an invitation
app.post('/invite_user', async (req, res) => {
  const { email } = req.body;

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ message: 'Valid email is required' });
  }

  try {
    let invite = await db.get('SELECT invite_id FROM invitations WHERE email = ?', email);

    if (!invite) {
      const invite_id = uuidv4();
      await db.run('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', email, invite_id);
      invite = { invite_id };
    }

    res.status(200).json({ invite_id: invite.invite_id, message: 'Invitation created or retrieved successfully' });
  } catch (error) {
    res.status(500).json({ message: 'Internal server error' });
  }
});

// Endpoint to create a user
app.post('/create_user', async (req, res) => {
  const { invite_id, user_name, password } = req.body;

  if (!invite_id || !user_name || !password) {
    return res.status(400).json({ message: 'Invite ID, username, and password are required' });
  }

  try {
    const invite = await db.get('SELECT email FROM invitations WHERE invite_id = ?', invite_id);

    if (!invite) {
      return res.status(401).json({ message: 'Invalid invite_id' });
    }

    const existingUser = await db.get('SELECT user_name FROM users WHERE user_name = ?', user_name);

    if (existingUser) {
      return res.status(400).json({ message: 'Username already exists. Try providing different username.' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    await db.run('INSERT INTO users (user_name, password) VALUES (?, ?)', user_name, hashedPassword);
    res.status(200).json({ message: 'User created successfully' });
  } catch (error) {
    res.status(500).json({ message: 'Internal server error' });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});