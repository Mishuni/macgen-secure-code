import fastify from 'fastify';
import { readFileSync } from 'fs';
import { join } from 'path';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';
import { escape } from 'html-escaper';

dotenv.config();

const app = fastify();
const dbFile = join(__dirname, 'db.sqlite3');
let db;

// Initialize SQLite database
async function initDb() {
  db = await open({
    filename: dbFile,
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      content TEXT NOT NULL,
      username TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
}

// Get all messages
app.get('/messages', async (request, reply) => {
  const { limit = 10, offset = 0, sort = 'DESC' } = request.query;

  // Validate query parameters
  const validSort = ['ASC', 'DESC'].includes(sort.toUpperCase()) ? sort.toUpperCase() : 'DESC';
  const validLimit = Number.isInteger(Number(limit)) && Number(limit) > 0 ? Number(limit) : 10;
  const validOffset = Number.isInteger(Number(offset)) && Number(offset) >= 0 ? Number(offset) : 0;

  try {
    const messages = await db.all(`
      SELECT * FROM messages
      ORDER BY created_at ${validSort}
      LIMIT ? OFFSET ?
    `, [validLimit, validOffset]);

    const escapedMessages = messages.map(msg => ({
      ...msg,
      content: escape(msg.content),
      username: escape(msg.username)
    }));

    reply
      .header('Content-Type', 'application/json; charset=utf-8')
      .send(escapedMessages);
  } catch (error) {
    reply.status(500).send({ error: 'Failed to retrieve messages' });
  }
});

// Post a new message
app.post('/messages', async (request, reply) => {
  const { content, username } = request.body;

  // Validate input
  if (typeof content !== 'string' || typeof username !== 'string' || !content.trim() || !username.trim()) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  // Additional input validation
  if (content.length > 500 || username.length > 100) {
    return reply.status(400).send({ error: 'Input exceeds maximum length' });
  }

  try {
    await db.run(`
      INSERT INTO messages (content, username)
      VALUES (?, ?)
    `, [content, username]);

    reply.send({ status: 'Message posted successfully' });
  } catch (error) {
    reply.status(500).send({ error: 'Failed to post message' });
  }
});

// Start the server
const start = async () => {
  try {
    await initDb();
    await app.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server listening on http://0.0.0.0:5000');
  } catch (err) {
    console.error(err);
    process.exit(1);
  }
};

start();